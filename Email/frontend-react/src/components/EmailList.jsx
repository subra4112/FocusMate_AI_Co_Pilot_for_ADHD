import PropTypes from "prop-types";

function EmailList({ emails, loading, onSelect, activeId }) {
  if (loading) {
    return <div className="empty-state">Loading emails…</div>;
  }

  if (!emails.length) {
    return <div className="empty-state">No emails found for this category.</div>;
  }

  return (
    <div className="email-list">
      {emails.map((email) => (
        <article
          key={email.message_id}
          className={`email-card ${activeId === email.message_id ? "selected" : ""}`}
        >
          <div>
            <h3>{email.subject}</h3>
            <p>{email.notes?.[0] ?? "No summary available."}</p>
          </div>
          <button type="button" onClick={() => onSelect(email)} aria-label="See report">
            >
          </button>
        </article>
      ))}
    </div>
  );
}

EmailList.propTypes = {
  emails: PropTypes.arrayOf(PropTypes.object),
  loading: PropTypes.bool,
  onSelect: PropTypes.func.isRequired,
  activeId: PropTypes.string,
};

EmailList.defaultProps = {
  emails: [],
  loading: false,
  activeId: null,
};

export default EmailList;

