import { useState, useEffect, useRef } from 'react';
import { Button } from '../components/ui/Button';
import { PaperPlaneRight, Robot, User, Plus, ChatText } from '@phosphor-icons/react';
import { clsx } from 'clsx';
import { PageHeader } from '../components/layout/PageHeader';
import { InvoicePreviewCard } from '../components/ui/InvoicePreviewCard';

interface ChatMessage {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  status: 'pending' | 'processing' | 'done';
  created_at: string;
  metadata?: string;
}

interface Conversation {
  conversation_id: string;
  title: string;
  updated_at: string;
}

export function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState(() => `conv-${Math.random().toString(36).substr(2, 9)}`);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isSending, setIsSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Load conversation list
  useEffect(() => {
    fetch('/api/chat/conversations')
      .then(r => r.json())
      .then(data => {
        if (data && data.conversations) {
          setConversations(data.conversations);
        }
      })
      .catch(console.error);
  }, [conversationId]); // Refresh list when conv changes

  useEffect(() => {
    fetch(`/api/chat/history/${conversationId}`)
      .then(r => r.json())
      .then(data => {
        if (data && data.messages) {
          setMessages(data.messages);
        }
      })
      .catch((err) => console.error("History fetch error:", err));
  }, [conversationId]);

  // Polling for new messages
  useEffect(() => {
    const poll = async () => {
      try {
        const lastId = messages.length > 0 ? Math.max(...messages.map(m => m.id)) : 0;
        const res = await fetch(`/api/chat/poll/${conversationId}?after=${lastId}`);
        const data = await res.json();
        if (data && data.has_new && data.messages.length > 0) {
          setMessages(prev => {
            const all = [...prev, ...data.messages];
            const unique = Array.from(new Map(all.map(m => [m.id, m])).values());
            return unique.sort((a, b) => a.id - b.id);
          });
          setIsSending(false); // Enable input once we get a response
        }
      } catch {
        // Silent poll error
      }
    };

    const interval = setInterval(poll, 1500);
    return () => clearInterval(interval);
  }, [conversationId, messages]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isSending) return;
    
    const text = input.trim();
    setInput('');
    setIsSending(true);

    // Optimistic UI update
    setMessages(prev => [...prev, {
      id: Date.now(), // temporary UI id
      role: 'user',
      content: text,
      status: 'pending',
      created_at: new Date().toISOString()
    }]);

    try {
      await fetch('/api/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ conversation_id: conversationId, message: text }) // NOTE: Backend expects 'message', not 'content'
      });
    } catch (err) {
      console.error(err);
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatText = (text: string) => {
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      }
      return <span key={i}>{part}</span>;
    });
  };

  const SUGGESTED_PROMPTS = [
    "What's my outstanding balance?",
    "Summarize my expenses this month",
    "List unpaid invoices",
    "Create an invoice for 45000 to Krishna Textiles"
  ];

  return (
    <div className="flex flex-col h-full animate-[fade-in_300ms_ease]">
      <PageHeader title="Chat with HERMES" breadcrumbs={false} />

      <div className="flex flex-1 overflow-hidden lg:mb-6 mb-0 gap-6">
        {/* Sidebar History */}
        <div className="hidden md:flex flex-col w-64 bg-bg-surface border border-border rounded-xl shadow-sm overflow-hidden">
          <div className="p-4 border-b border-border">
            <Button 
              variant="primary" 
              className="w-full flex items-center justify-center gap-2"
              onClick={() => setConversationId(`conv-${Math.random().toString(36).substr(2, 9)}`)}
            >
              <Plus size={16} weight="bold" /> New Chat
            </Button>
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-1 style-scrollbar">
            {conversations.map(c => (
              <button
                key={c.conversation_id}
                onClick={() => setConversationId(c.conversation_id)}
                className={clsx(
                  "w-full text-left px-3 py-2 rounded-lg text-[13px] transition-colors flex items-center gap-2 truncate",
                  conversationId === c.conversation_id 
                    ? "bg-accent-subtle text-accent font-medium" 
                    : "text-text-secondary hover:bg-bg-overlay hover:text-text-primary"
                )}
              >
                <ChatText size={16} className="shrink-0" />
                <span className="truncate">{c.title || c.conversation_id}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="flex flex-col flex-1 border border-border rounded-xl bg-bg-surface overflow-hidden shadow-sm">
          <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 style-scrollbar bg-bg-screen">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-text-muted space-y-4">
                <div className="w-16 h-16 bg-accent-subtle rounded-full flex items-center justify-center">
                  <Robot size={32} className="text-accent" weight="duotone" />
                </div>
                <p className="text-[16px] font-medium text-text-primary">How can I help you today?</p>
                <div className="flex gap-2 flex-wrap justify-center mt-6 max-w-md">
                  {SUGGESTED_PROMPTS.map(p => (
                    <button 
                      key={p} 
                      onClick={() => { setInput(p); inputRef.current?.focus(); }}
                      className="px-4 py-2 text-[13px] bg-bg-surface hover:bg-bg-overlay rounded-full transition-colors border border-border text-text-primary shadow-sm"
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((msg, idx) => {
                let metadataObj = null;
                if (msg.metadata) {
                  try {
                    metadataObj = JSON.parse(msg.metadata);
                  } catch (e) {}
                }

                return (
                  <div key={msg.id || idx} className={clsx("flex gap-3 animate-[fade-in-up_200ms_ease]", msg.role === 'user' ? "flex-row-reverse" : "")}>
                    <div className={clsx("w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1", msg.role === 'user' ? "bg-accent text-white" : "bg-bg-overlay text-text-secondary")}>
                      {msg.role === 'user' ? <User size={16} /> : <Robot size={18} />}
                    </div>
                    <div className="flex flex-col gap-1 max-w-[85%] md:max-w-[75%]">
                      <div className={clsx("rounded-2xl px-5 py-3 whitespace-pre-wrap text-[14px]", msg.role === 'user' ? "bg-accent text-white rounded-tr-sm" : "bg-bg-surface border border-border text-text-primary rounded-tl-sm shadow-sm")}>
                        {formatText(msg.content)}
                      </div>
                      
                      {/* Inline Invoice Preview Card if metadata exists */}
                      {metadataObj && metadataObj.invoice_id && (
                        <InvoicePreviewCard 
                          invoiceId={metadataObj.invoice_id} 
                          type="invoice" 
                          amount={metadataObj.amount} 
                          contactName={metadataObj.contact_name} 
                        />
                      )}
                      {metadataObj && metadataObj.bill_id && (
                        <InvoicePreviewCard 
                          invoiceId={metadataObj.bill_id} 
                          type="bill" 
                          amount={metadataObj.amount} 
                          contactName={metadataObj.contact_name} 
                        />
                      )}
                    </div>
                  </div>
                );
              })
            )}
            
            {isSending && (
              <div className="flex gap-3 animate-[fade-in_200ms_ease]">
                <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 bg-bg-overlay text-text-secondary">
                  <Robot size={18} />
                </div>
                <div className="rounded-2xl px-5 py-4 bg-bg-surface border border-border rounded-tl-sm shadow-sm flex gap-1 items-center">
                  <div className="w-1.5 h-1.5 rounded-full bg-text-muted animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-1.5 h-1.5 rounded-full bg-text-muted animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-1.5 h-1.5 rounded-full bg-text-muted animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            )}
            
            <div ref={bottomRef} className="h-1" />
          </div>

          <div className="p-3 md:p-4 bg-bg-surface border-t border-border">
            <div className="flex gap-2 items-end">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask HERMES..."
                className="flex-1 max-h-[140px] min-h-[44px] bg-bg-overlay border border-border rounded-xl px-4 py-3 text-[14px] text-text-primary resize-none focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent style-scrollbar transition-all"
                rows={1}
                disabled={isSending}
              />
              <Button 
                onClick={handleSend} 
                disabled={!input.trim() || isSending}
                className="h-[44px] w-[44px] shrink-0 p-0 flex items-center justify-center rounded-xl transition-transform active:scale-95"
              >
                <PaperPlaneRight size={20} weight="fill" />
              </Button>
            </div>
            <div className="text-[12px] text-center text-text-muted mt-3">
              HERMES AI can make mistakes. Please verify important financial answers.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
