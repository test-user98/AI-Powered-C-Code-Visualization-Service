import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

function MermaidDiagram({ chart }) {
  const elementRef = useRef(null);
  const idRef = useRef(`mermaid-${Math.random().toString(36).substr(2, 9)}`);

  useEffect(() => {
    if (chart && elementRef.current) {
      // Initialize mermaid with basic config
      mermaid.initialize({
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'loose',
        fontFamily: 'arial',
        fontSize: 14
      });

      // Clear previous content
      elementRef.current.innerHTML = '';

      // Render the chart
      mermaid.render(idRef.current, chart)
        .then((result) => {
          elementRef.current.innerHTML = result.svg;
        })
        .catch((error) => {
          console.error('Mermaid render error:', error);
          elementRef.current.innerHTML = `<div style="color: red; padding: 10px;">Error rendering diagram: ${error.message}</div>`;
        });
    }
  }, [chart]);

  return (
    <div className="mermaid-container">
      <div ref={elementRef} style={{ minHeight: '200px' }}>
        {chart ? 'Loading diagram...' : 'No diagram data'}
      </div>
    </div>
  );
}

export default MermaidDiagram;
