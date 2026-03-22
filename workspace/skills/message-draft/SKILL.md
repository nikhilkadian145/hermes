---
name: message-draft
description: Draft professional business messages, emails, or WhatsApp texts for the owner. Use when the user asks "message draft karo", "email likhne mein help karo", "professional message chahiye", "follow up message banao", "Raj ko kya likhun", "WhatsApp message banana hai", or needs help composing any business communication (not payment reminders — use reminder-draft for those).
---

# Message Draft

Write professional business messages in the right tone for any situation.

## Use Cases

| Situation | Example |
|---|---|
| Project update | Tell client work is in progress |
| Delay apology | Deadline miss ho gayi, apologize |
| Work completion | Job done, invoice incoming |
| Meeting request | Fix a meeting with client |
| Proposal follow-up | Quote bheja tha, koi reply nahi |
| Complaint response | Client unhappy, respond professionally |
| Introduction | New client ko introduce yourself |
| Thank you | After large payment or project |
| Scope change | Work badh gaya, more cost |

## Information to Collect

1. **Purpose** — what's the message about?
2. **Recipient** — client name (to personalize)
3. **Key points** — what must the message include?
4. **Tone** — Friendly / Professional / Apologetic / Firm
5. **Language** — Hinglish (default) / Pure Hindi / English

## Drafting Process

```
1. Understand situation from user
2. Identify tone + recipient
3. DbGetClientTool(name)   → personalize with their name, history
4. Draft message
5. Show to user for review / edits
```

## Draft Format

Always show as a clean copyable block:

```
📝 Message Draft:
─────────────────────────────────────
Namaste Raj ji! 🙏

Aapka website redesign project ka kaam
achha progress kar raha hai. Main expect
kar raha hoon ki basic structure is week
ke end tak ready ho jayega.

Koi bhi sawaal ho to freely pooch sakte hain.

Dhanyawad!
[Your Name]
[Business Name] | [Phone]
─────────────────────────────────────
Copy karein ya edit karein?
```

## Tone Examples

**Friendly (Hinglish):**
Conversational, warm, uses "ji", "dhanyawad", emojis sparingly

**Professional (English):**
Formal, complete sentences, no Hinglish, salutation + closing

**Apologetic:**
Acknowledge mistake first, then solution, end positively

**Firm:**
Direct, no fluff, clear ask/deadline, polite but unambiguous

## Scope Change Message (Special)

When user needs to tell client work scope increased:
```
Namaste [Client] ji,

Aapke project mein kuch additional requirements
samne aayi hain jo original scope se bahar hain:

- [Requirement 1]
- [Requirement 2]

Iske liye additional ₹[amount] aur [X days]
lagenge. Aage badhne se pehle aapki approval
chahiye.

Please confirm kar dein.
Dhanyawad!
```

## After Draft Approved

"Copy karo aur WhatsApp pe paste kar do — ya HERMES sirf drafts banata hai, seedha nahi bhej sakta (client ka number available nahi hai)."

Offer to save draft: "Ye draft save karoon agar baad mein kaam aaye?"
