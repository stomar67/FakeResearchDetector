function PaperMetadata({ paper }) {
  if (!paper) {
    return null
  }

  return (
    <section>
      <h2>Paper Metadata</h2>

      <p>
        <strong>Paper ID:</strong> {paper.paper_id}
      </p>

      <p>
        <strong>Variant ID:</strong> {paper.variant_id}
      </p>

      <p>
        <strong>Filename:</strong> {paper.filename}
      </p>

      <p>
        <strong>Title:</strong> {paper.title || 'Not available'}
      </p>

      <p>
        <strong>Created At:</strong> {paper.created_at}
      </p>
    </section>
  )
}

export default PaperMetadata