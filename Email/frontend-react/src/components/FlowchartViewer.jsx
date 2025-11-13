import PropTypes from "prop-types";

function FlowchartViewer({ source, type }) {
  if (!source) {
    return <p>No flowchart available.</p>;
  }

  if (type === "json") {
    let steps = [];
    try {
      const parsed = JSON.parse(source);
      steps = parsed.steps || [];
    } catch (err) {
      console.error("Flowchart parse error", err);
      return <pre className="flowchart-box">{source}</pre>;
    }

    if (!steps.length) {
      return <p>No steps found.</p>;
    }

    return (
      <div className="flowchart-timeline">
        {steps.map((step, index) => (
          <div key={index} className="timeline-step">
            <div className="timeline-index">{index + 1}</div>
            <div className="timeline-content">
              <h4>Step {index + 1}</h4>
              <p>{step}</p>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return <pre className="flowchart-box">{source}</pre>;
}

FlowchartViewer.propTypes = {
  source: PropTypes.string,
  type: PropTypes.string,
};

FlowchartViewer.defaultProps = {
  source: null,
  type: null,
};

export default FlowchartViewer;
