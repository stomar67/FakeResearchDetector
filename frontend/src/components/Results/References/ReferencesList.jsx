function ReferencesList({ references }) {
  if (!references || references.length === 0) {
    return (
      <section>
        <h2>References</h2>
        <p>No references available.</p>
      </section>
    )
  }

  return (
    <section>
      <h2>References</h2>

      {references.map((reference) => (
        <article key={reference.id}>
          <h3>
            Reference {reference.reference_number}
          </h3>

          {reference.reference_identifier && (
            <p>
              <strong>Identifier:</strong>{' '}
              {reference.reference_identifier}
            </p>
          )}

          {reference.page_number && (
            <p>
              <strong>Page:</strong>{' '}
              {reference.page_number}
            </p>
          )}

          <p>
            <strong>Reference:</strong>{' '}
            {reference.raw_text}
          </p>
        </article>
      ))}
    </section>
  )
}

export default ReferencesList