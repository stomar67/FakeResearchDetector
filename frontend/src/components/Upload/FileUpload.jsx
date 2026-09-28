import { useState } from 'react'
import { validatePDF } from '../../utils/fileValidation'

function FileUpload({ onUpload }) {
  const [file, setFile] = useState(null)
  const [error, setError] = useState('')

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0]

    setError('')
    setFile(null)

    if (!selectedFile) {
      return
    }

    const validation = validatePDF(selectedFile)

    if (!validation.valid) {
      setError(validation.message)
      return
    }

    setFile(selectedFile)
  }

  const handleUpload = () => {
    if (!file) {
      setError('Please select a PDF file first.')
      return
    }

    onUpload(file)
  }

  return (
    <div>
      <h2>Upload Research Paper</h2>

      <p>Select a research paper in PDF format.</p>

      <input
        type="file"
        accept=".pdf,application/pdf"
        onChange={handleFileChange}
      />

      {file && (
        <p>
          Selected file: <strong>{file.name}</strong>
        </p>
      )}

      {error && (
        <p role="alert">
          {error}
        </p>
      )}

      <button
        type="button"
        onClick={handleUpload}
        disabled={!file}
      >
        Upload & Analyze
      </button>
    </div>
  )
}

export default FileUpload
