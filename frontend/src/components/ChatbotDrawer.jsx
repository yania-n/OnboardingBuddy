import React, { useState, useEffect, useRef } from 'react';
import { 
  MessageSquare, 
  Send, 
  Sparkles, 
  User, 
  Bot, 
  AlertCircle, 
  ExternalLink, 
  FileText, 
  X, 
  ChevronRight,
  Maximize2,
  Minimize2,
  HelpCircle
} from 'lucide-react';
import { sendChatMessage, fetchChatHistory } from '../api/client';

const SUGGESTED_QUESTIONS = [
  "What tools and system access do I need on Day 1?",
  "What is our Vehicle-to-Grid (V2G) closed-loop synergy?",
  "What are our core operating principles?",
  "Who is my executive leader and what is our reporting structure?",
  "What is the SLA for Snowflake and Data Governance approval?",
  "What is the policy for personal pets in testing labs?" // tests fallback!
];

export default function ChatbotDrawer({ selectedJoiner, onOpenDoc, onClose }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const messagesEndRef = useRef(null);

  // Load chat history when joiner changes
  useEffect(() => {
    async function loadHistory() {
      if (!selectedJoiner?.id) return;
      try {
        const history = await fetchChatHistory(selectedJoiner.id);
        if (history && history.length > 0) {
          setMessages(history);
        } else {
          // Add initial welcome greeting
          setMessages([
            {
              id: 'welcome',
              role: 'assistant',
              content: `Hello ${selectedJoiner.name}! 👋 I am your AI Onboarding Assistant. I can answer any questions about your role as ${selectedJoiner.role} in ${selectedJoiner.department} (${selectedJoiner.business_unit}), company policies, tools, access provisioning, or team workflows. Everything I say is strictly grounded in our knowledge base!`,
              citations: [],
              is_missing_info: false
            }
          ]);
        }
      } catch (e) {
        console.error(e);
      }
    }
    loadHistory();
  }, [selectedJoiner?.id]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (textToSend) => {
    const queryText = textToSend || input;
    if (!queryText.trim() || loading) return;

    const userMsg = {
      id: Date.now().toString(),
      role: 'user',
      content: queryText.trim(),
      created_at: new Date().toISOString()
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const resp = await sendChatMessage(queryText.trim(), selectedJoiner?.id);
      const assistantMsg = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: resp.answer,
        citations: resp.citations || [],
        is_missing_info: resp.is_missing_info,
        manager_escalation: resp.manager_escalation,
        created_at: new Date().toISOString()
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: 'Sorry, I encountered an error communicating with the AI service. Please try again.',
          is_missing_info: false
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`fixed bottom-4 right-4 z-40 bg-white rounded-2xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden transition-all duration-300 ${
      expanded ? 'w-[680px] h-[720px]' : 'w-[420px] h-[560px]'
    }`}>
      
      {/* Drawer Header */}
      <div className="px-5 py-3.5 bg-gradient-to-r from-slate-900 to-slate-800 text-white flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-brand-500 flex items-center justify-center text-white shadow-inner">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-sm leading-tight flex items-center gap-1.5">
              Q&A Onboarding Assistant
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            </h3>
            <p className="text-[11px] text-slate-300">Grounded in Knowledge Base</p>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-1.5 text-slate-300 hover:text-white hover:bg-slate-700/50 rounded-lg transition-colors"
            title={expanded ? "Minimize window" : "Expand window"}
          >
            {expanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="p-1.5 text-slate-300 hover:text-white hover:bg-slate-700/50 rounded-lg transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 p-4 overflow-y-auto bg-slate-50/60 space-y-4">
        {messages.map((msg, index) => (
          <div
            key={msg.id || index}
            className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'assistant' && (
              <div className="w-7 h-7 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center flex-shrink-0 mt-0.5 border border-brand-200">
                <Bot className="w-4 h-4" />
              </div>
            )}

            <div className={`max-w-[85%] rounded-2xl p-3.5 text-xs shadow-sm leading-relaxed ${
              msg.role === 'user'
                ? 'bg-brand-600 text-white rounded-br-none'
                : msg.is_missing_info
                ? 'bg-amber-50 border border-amber-200 text-slate-800 rounded-bl-none'
                : 'bg-white border border-slate-200 text-slate-800 rounded-bl-none'
            }`}>
              
              {/* Missing Info Warning Callout */}
              {msg.is_missing_info && (
                <div className="flex items-center gap-1.5 text-amber-800 font-semibold mb-2 pb-1.5 border-b border-amber-200">
                  <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0" />
                  <span>Unanswered in KB - Escalated to Manager</span>
                </div>
              )}

              {/* Message text with whitespace formatting */}
              <div className="whitespace-pre-wrap font-sans">
                {msg.content}
              </div>

              {/* Citations Badges */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-3 pt-2.5 border-t border-slate-100">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1.5">
                    Grounded Sources & Citations:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {msg.citations.map((cit, cIdx) => (
                      <button
                        key={cIdx}
                        onClick={() => onOpenDoc(`${cit.doc_name}#${cit.section_title}`)}
                        className="inline-flex items-center gap-1 px-2 py-1 rounded bg-slate-100 hover:bg-brand-50 hover:text-brand-700 hover:border-brand-200 text-[11px] font-medium text-slate-700 border border-slate-200 transition-colors"
                        title={cit.excerpt}
                      >
                        <FileText className="w-3 h-3 text-slate-400" />
                        <span className="truncate max-w-[160px]">{cit.doc_name}</span>
                        <ExternalLink className="w-2.5 h-2.5 opacity-60" />
                      </button>
                    ))}
                  </div>
                </div>
              )}

            </div>

            {msg.role === 'user' && (
              <div className="w-7 h-7 rounded-full bg-slate-800 text-white flex items-center justify-center flex-shrink-0 mt-0.5 shadow-sm">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-3 justify-start items-center">
            <div className="w-7 h-7 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center flex-shrink-0 border border-brand-200">
              <Bot className="w-4 h-4 animate-spin" />
            </div>
            <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-none px-4 py-2.5 text-xs text-slate-500 flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-brand-500 animate-ping"></span>
              Searching knowledge base & synthesizing answer...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Quick Questions Bar */}
      <div className="px-3 py-2 bg-slate-100 border-t border-slate-200 overflow-x-auto whitespace-nowrap flex gap-1.5 no-scrollbar">
        {SUGGESTED_QUESTIONS.map((q, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(q)}
            disabled={loading}
            className="text-[11px] font-medium bg-white hover:bg-brand-50 hover:text-brand-700 text-slate-600 px-2.5 py-1 rounded-full border border-slate-200 shadow-2xs transition-colors flex-shrink-0"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input Box */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="p-3 bg-white border-t border-slate-200 flex items-center gap-2"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={`Ask anything about ${selectedJoiner?.role || 'onboarding'}...`}
          className="flex-1 px-3.5 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 focus:bg-white text-slate-800"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="p-2 bg-brand-600 hover:bg-brand-700 disabled:opacity-40 text-white rounded-xl shadow-sm transition-all"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>

    </div>
  );
}
