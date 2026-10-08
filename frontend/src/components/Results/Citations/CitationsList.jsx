function CitationsList({ citations }) {
  if (!citations || citations.length === 0) {
    return (
      <section>
        <h2>Citations</h2>
        <p>No citations available.</p>
      </section>
    )
  }

  return (
    <section>
      <h2>Citations</h2>

      {citations.map((citation) => (
        <article key={citation.id}>
          <h3>Citation {citation.id}</h3>

          <p>
            <strong>Citation:</strong> {citation.citation_text}
          </p>

          {citation.claim_id && (
            <p>
              <strong>Claim ID:</strong> {citation.claim_id}
            </p>
          )}

          {citation.reference_id && (
            <p>
              <strong>Reference ID:</strong> {citation.reference_id}
            </p>
          )}

          {citation.page_number && (
            <p>
              <strong>Page:</strong> {citation.page_number}
            </p>
          )}
        </article>
      ))}
    </section>
  )
}

export default CitationsList