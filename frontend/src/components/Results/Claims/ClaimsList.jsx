
function ClaimsList({ claims }) {
  if (!claims || claims.length === 0) {
    return (
      <section>
        <h2>Claims</h2>
        <p>No claims available.</p>
      </section>
    )
  }

  return (
    <section>
      <h2>Claims</h2>

      {claims.map((claim) => (
        <article key={claim.id}>
          <h3>Claim {claim.id}</h3>

          <p>
            <strong>Claim:</strong> {claim.text}
          </p>

          {claim.claim_type && (
            <p>
              <strong>Type:</strong> {claim.claim_type}
            </p>
          )}

          {claim.page_number !== null &&
            claim.page_number !== undefined && (
              <p>
                <strong>Page:</strong> {claim.page_number}
              </p>
            )}

          {claim.section_id !== null &&
            claim.section_id !== undefined && (
              <p>
                <strong>Section ID:</strong> {claim.section_id}
              </p>
            )}

          {Array.isArray(claim.citation_ids) && (
            <p>
              <strong>Citation IDs:</strong>{' '}
              {claim.citation_ids.length > 0
                ? claim.citation_ids.join(', ')
                : 'None'}
            </p>
          )}
        </article>
      ))}
    </section>
  )
}

export default ClaimsList

