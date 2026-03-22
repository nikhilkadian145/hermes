import os
import zipfile
from unittest.mock import patch, MagicMock
from pathlib import Path
from tempfile import TemporaryDirectory

from hermes.export import create_ca_bundle, export_table_to_csv

# We'll mock the hermes.db functions so we don't need a real DB setup.
@patch("hermes.export.get_business")
@patch("hermes.export.get_pl_summary")
@patch("hermes.export.get_gst_report")
@patch("hermes.export.get_outstanding_report")
@patch("hermes.export.list_invoices")
@patch("hermes.export.list_expenses")
@patch("hermes.export.export_table_to_csv")
@patch("hermes.export.generate_pl_report_pdf")
@patch("hermes.export.generate_gst_report_pdf")
@patch("hermes.export.generate_outstanding_report_pdf")
def test_create_ca_bundle(
    mock_gen_out, mock_gen_gst, mock_gen_pl,
    mock_export_csv, mock_list_exp, mock_list_inv,
    mock_get_out, mock_get_gst, mock_get_pl, mock_get_bz
):
    # Setup Mocks
    mock_get_bz.return_value = {"name": "Acme Corp"}
    mock_list_inv.return_value = [{"invoice_number": "INV-001", "issue_date": "2023-10-15"}]
    
    with TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        # Create a dummy receipt file to be picked up
        receipt_path = tmp / "expenses" / "receipts" / "dummy_receipt.jpg"
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text("fake image data")
        
        mock_list_exp.return_value = [{"receipt_path": str(receipt_path)}]
        
        # Create dummy invoice PDF to be picked up
        invoices_dir = tmp / "invoices"
        invoices_dir.mkdir(parents=True, exist_ok=True)
        inv_pdf = invoices_dir / "INV-001.pdf"
        inv_pdf.write_text("fake pdf data")
        
        # Make the mock PDF generators actually touch the output files so the zip doesn't crash on FileNotFoundError
        def mock_pdf_generator(*args):
            # The output path is the last argument or specified
            path = args[-1]
            Path(path).write_text("fake pdf content")
            return path
            
        mock_gen_pl.side_effect = mock_pdf_generator
        mock_gen_gst.side_effect = mock_pdf_generator
        mock_gen_out.side_effect = mock_pdf_generator
        
        # Let mock_export_csv touch files
        def mock_csv(*args):
            path = args[-1]
            Path(path).write_text("col1,col2\n1,2")
            
        mock_export_csv.side_effect = mock_csv
        
        
        output_zip = str(tmp / "bundle.zip")
        db_path = str(tmp / "dummy.db")
        Path(db_path).write_text("")  # create empty db file just so exists() passes
        
        # Execute Export
        result = create_ca_bundle(
            db_path=db_path,
            customer_data_dir=str(tmp),
            from_date="2023-10-01",
            to_date="2023-10-31",
            output_path=output_zip
        )
        
        assert result["success"] is True
        assert os.path.exists(output_zip)
        
        # Verify ZIP Contents
        with zipfile.ZipFile(output_zip, "r") as zf:
            files = zf.namelist()
            assert "summary/pl_report.pdf" in files
            assert "summary/gst_report.pdf" in files
            assert "summary/outstanding.pdf" in files
            assert "data/invoices.csv" in files
            assert "data/payments.csv" in files
            assert "data/expenses.csv" in files
            assert "README.txt" in files
            assert "invoices/INV-001.pdf" in files
            assert "expenses/receipts/dummy_receipt.jpg" in files
