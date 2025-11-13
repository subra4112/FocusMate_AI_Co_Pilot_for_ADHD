import { useState } from "react";
import PropTypes from "prop-types";

function FollowUpChat({ messages, loading, error, onAsk, suggestion }) {
  const [input, setInput] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!input.trim()) {
      return;
    }
    onAsk(input.trim());
    setInput("");
  };

  const handleSuggestion = () => {
    if (!suggestion) {
      return;
    }
    onAsk(suggestion);
  };

  return (
    <div className="followup-panel">
      <div className="followup-log">
        {messages.length === 0 ? (
          <p className="placeholder">Ask a question about your inbox to get started.</p>
        ) : (
          messages.map((entry, index) => (
            <div key={`${entry.role}-${index}`} className={`chat-row ${entry.role}`}>
              <div className="chat-bubble">
                {entry.text.split("\n").map((line, idx) => (
                  <p key={`${entry.role}-${index}-line-${idx}`}>{line}</p>
                ))}
                {entry.role === "assistant" && entry.references?.length ? (
                  <p className="chat-meta">References: {entry.references.join(", ")}</p>
                ) : null}
                {entry.role === "assistant" && entry.followUp ? (
                  <p className="chat-meta">Suggested follow-up: “{entry.followUp}”</p>
                ) : null}
              </div>
            </div>
          ))
        )}
      </div>

      {error ? <p className="chat-error">{error}</p> : null}

      <form className="followup-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask about your emails, summaries, or calendar tasks…"
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          {loading ? "Thinking…" : "Ask"}
        </button>
        <button
          type="button"
          className="ghost"
          onClick={handleSuggestion}
          disabled={loading || !suggestion}
        >
          Use suggestion
        </button>
      </form>
    </div>
  );
}

FollowUpChat.propTypes = {
  messages: PropTypes.arrayOf(
    PropTypes.shape({
      role: PropTypes.oneOf(["user", "assistant"]).isRequired,
      text: PropTypes.string.isRequired,
      followUp: PropTypes.string,
      references: PropTypes.arrayOf(PropTypes.string),
    })
  ).isRequired,
  loading: PropTypes.bool,
  error: PropTypes.string,
  onAsk: PropTypes.func.isRequired,
  suggestion: PropTypes.string,
};

FollowUpChat.defaultProps = {
  loading: false,
  error: null,
  suggestion: null,
};

export default FollowUpChat;
