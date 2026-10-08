function SectionViewer({ sections }) {
  if (!sections || sections.length === 0) {
    return (
      <section>
        <h2>Sections</h2>
        <p>No sections available.</p>
      </section>
    )
  }

  return (
    <section>
      <h2>Sections</h2>

      {sections.map((section) => (
        <article key={section.id}>
          <h3>
            {section.order}. {section.name}
          </h3>

          <p>
            Pages: {section.page_start}–{section.page_end}
          </p>

          <p>{section.content}</p>
        </article>
      ))}
    </section>
  )
}

export default SectionViewer