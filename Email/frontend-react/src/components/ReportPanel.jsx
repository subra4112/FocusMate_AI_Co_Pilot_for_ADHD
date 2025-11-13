import PropTypes from "prop-types";
import FlowchartViewer from "./FlowchartViewer.jsx";

const FALLBACK_IMAGE = "https://images.unsplash.com/photo-1498050108023-c5249f4df085";

function ReportPanel({ email, category }) {
  if (!email) {
    return (
      <div className="report-panel">
        <h2>Select an email to see the report</h2>
        <p className="muted">
          Choose a card on the left to preview the calendar link, article summary, or instruction flowchart.
        </p>
      </div>
    );
  }

  return (
    <div className="report-panel">
      <header className="report-header">
        <h2>{email.subject}</h2>
        <span className="chip">{category}</span>
      </header>
      <section className="report-section">
        <h3>Summary</h3>
        <p>{email.notes?.find((note) => note.startsWith("Summary"))?.replace("Summary: ", "") ?? "No summary available."}</p>
      </section>

      {category === "task" && (
        <section className="report-section">
          <h3>Calendar</h3>
          <p>
            {email.notes?.find((note) => note.toLowerCase().startsWith("acknowledgement")) ??
              "Task captured without calendar event."}
          </p>
          {email.calendar_event_link ? (
            <p className="muted">
              {email.notes?.find((note) => note.toLowerCase().startsWith("calendar link")) ??
                `Calendar event available.`}
            </p>
          ) : null}
          <button
            type="button"
            className="primary-btn"
            onClick={() => email.calendar_event_link && window.open(email.calendar_event_link, "_blank")}
            disabled={!email.calendar_event_link}
          >
            {email.calendar_event_link ? "Open Calendar Link" : "No calendar event"}
          </button>
        </section>
      )}

      {category === "article" && (
        <section className="report-section">
          <h3>Theme Visual</h3>
          <div className="theme-image">
            <img src={email.theme_image || FALLBACK_IMAGE} alt="Theme" />
          </div>
        </section>
      )}

      {category === "instruction" && email.flowchart && (
        <section className="report-section">
          <h3>Flowchart</h3>
          <FlowchartViewer source={email.flowchart} type={email.flowchart_type} />
        </section>
      )}

      <section className="report-section">
        <h3>Priority</h3>
        <p>
          Bucket: <strong>{email.priority_bucket}</strong> · Score: <strong>{email.priority_score}</strong>
        </p>
        <p className="muted">{email.priority_reasoning}</p>
      </section>
    </div>
  );
}

ReportPanel.propTypes = {
  email: PropTypes.shape({
    message_id: PropTypes.string,
    subject: PropTypes.string,
    notes: PropTypes.arrayOf(PropTypes.string),
    theme_image: PropTypes.string,
    flowchart: PropTypes.string,
    flowchart_type: PropTypes.string,
    priority_bucket: PropTypes.string,
    priority_score: PropTypes.number,
    priority_reasoning: PropTypes.string,
    calendar_event_link: PropTypes.string,
  }),
  category: PropTypes.string.isRequired,
};

ReportPanel.defaultProps = {
  email: null,
};

export default ReportPanel;

