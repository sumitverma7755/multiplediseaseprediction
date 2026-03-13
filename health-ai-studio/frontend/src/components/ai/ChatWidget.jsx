import { useState } from 'react';
import { MessageCircle, SendHorizontal } from 'lucide-react';
import { askAssistant } from '../../services/assistantService';

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'Ask Health AI: I can explain predictions, answer basic health questions, and suggest lifestyle improvements.'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const send = async () => {
    if (!input.trim() || loading) {
      return;
    }

    const nextMessages = [...messages, { role: 'user', text: input.trim() }];
    setMessages(nextMessages);
    setInput('');
    setLoading(true);

    try {
      const response = await askAssistant({
        question: input.trim(),
        context: 'healthcare-dashboard'
      });
      setMessages((current) => [...current, { role: 'assistant', text: response.answer }]);
    } catch (error) {
      setMessages((current) => [...current, { role: 'assistant', text: error.message }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-5 right-5 z-40">
      {open ? (
        <div className="mb-3 w-[340px] overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-panel">
          <div className="flex items-center justify-between bg-brand-700 px-4 py-3 text-white">
            <h4 className="text-sm font-semibold">Ask Health AI</h4>
            <button onClick={() => setOpen(false)} className="text-sm">Close</button>
          </div>
          <div className="h-72 space-y-3 overflow-y-auto bg-slate-50 p-3 scrollbar-thin">
            {messages.map((message, idx) => (
              <div
                key={`${message.role}-${idx}`}
                className={`max-w-[90%] rounded-xl px-3 py-2 text-sm ${
                  message.role === 'user'
                    ? 'ml-auto bg-brand-700 text-white'
                    : 'bg-white text-slate-700 border border-slate-200'
                }`}
              >
                {message.text}
              </div>
            ))}
          </div>
          <div className="flex items-center gap-2 border-t border-slate-200 p-3">
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter') {
                  event.preventDefault();
                  send();
                }
              }}
              placeholder="Ask about prediction or lifestyle improvements"
              className="flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm"
            />
            <button
              onClick={send}
              disabled={loading}
              className="inline-flex items-center rounded-lg bg-brand-700 p-2 text-white disabled:opacity-70"
            >
              <SendHorizontal className="h-4 w-4" />
            </button>
          </div>
        </div>
      ) : null}

      <button
        onClick={() => setOpen((state) => !state)}
        className="inline-flex items-center gap-2 rounded-full bg-brand-700 px-4 py-3 text-sm font-semibold text-white shadow-panel hover:bg-brand-800"
      >
        <MessageCircle className="h-4 w-4" />
        Ask Health AI
      </button>
    </div>
  );
}
