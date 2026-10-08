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
            <strong>Claim:</strong> {claim.claim_text}
          </p>

          {claim.claim_type && (
            <p>
              <strong>Type:</strong> {claim.claim_type}
            </p>
          )}

          {claim.page_number && (
            <p>
              <strong>Page:</strong> {claim.page_number}
            </p>
          )}
        </article>
      ))}
    </section>
  )
}

export default ClaimsList