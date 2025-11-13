import { useMemo, useState } from "react";
import EmailList from "./components/EmailList.jsx";
import ReportPanel from "./components/ReportPanel.jsx";
import FollowUpChat from "./components/FollowUpChat.jsx";
import useEmails from "./hooks/useEmails.js";
import useFollowUpChat from "./hooks/useFollowUpChat.js";

const CATEGORIES = [
  { key: "task", label: "Tasks" },
  { key: "article", label: "Articles" },
  { key: "instruction", label: "Instructions" },
];

function App() {
  const { data, loading, error, refetch } = useEmails();
  const { messages, loading: chatLoading, error: chatError, ask, suggestion } = useFollowUpChat();
  const [activeCategory, setActiveCategory] = useState("task");
  const [selectedEmail, setSelectedEmail] = useState(null);

  const emailsForCategory = useMemo(() => data[activeCategory] ?? [], [data, activeCategory]);

  const handleCategoryChange = (category) => {
    setActiveCategory(category);
    setSelectedEmail(null);
  };

  const handleSelectEmail = (email) => {
    setSelectedEmail(email);
  };

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="brand">
          <h1>FocusMate Inbox</h1>
          <button className="refresh" onClick={refetch} disabled={loading}>
            {loading ? "Refreshing…" : "Refresh"}
          </button>
        </div>
        <nav className="nav">
          {CATEGORIES.map(({ key, label }) => (
            <button
              key={key}
              className={`nav-btn ${activeCategory === key ? "active" : ""}`}
              onClick={() => handleCategoryChange(key)}
              disabled={loading}
            >
              {label}
              <span className="pill">{(data[key] ?? []).length}</span>
            </button>
          ))}
        </nav>
        {error ? <p className="error">{error}</p> : null}
      </aside>

      <div className="content-wrapper">
        <main className="content">
          <section className="list-container">
            <EmailList
              emails={emailsForCategory}
              loading={loading}
              onSelect={handleSelectEmail}
              activeId={selectedEmail?.message_id}
            />
          </section>
          <section className="report-container">
            <ReportPanel email={selectedEmail} category={activeCategory} />
          </section>
        </main>
        <section className="followup-section">
          <h2>Follow-up Q&A</h2>
          <FollowUpChat
            messages={messages}
            loading={chatLoading}
            error={chatError}
            onAsk={ask}
            suggestion={suggestion}
          />
        </section>
      </div>
    </div>
  );
}

export default App;
