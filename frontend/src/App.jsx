import { useState } from 'react'
import UploadPage from './pages/UploadPage'
import UploadStatus from './components/Upload/UploadStatus'
import {
  uploadResearchPaper,
  analyzeResearchPaper,
  getPaperResults,
} from './services/api'

function App() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [status, setStatus] = useState('idle')
  const [message, setMessage] = useState('')
  const [analysisResult, setAnalysisResult] = useState(null)

  const handleUpload = async (file) => {
    setSelectedFile(file)
    setStatus('uploading')
    setMessage('')
    setAnalysisResult(null)

    try {
      const uploadResult = await uploadResearchPaper(file)

      const paperId = uploadResult?.paper?.id

      if (!paperId) {
        throw new Error(
          'Upload succeeded, but no paper ID was returned by the backend.',
        )
      }

      setStatus('processing')

      const analysisResult = await analyzeResearchPaper(paperId)

const paperResults = await getPaperResults(paperId)

setAnalysisResult(paperResults)
setStatus('success')
setMessage(
  analysisResult?.message ||
    'Paper analysis completed successfully.',
)
      
    } catch (error) {
      console.error('Paper upload/analysis failed:', error)

      const backendMessage =
        error?.response?.data?.detail ||
        error?.response?.data?.message

      setStatus('error')
      setMessage(
        backendMessage ||
          error.message ||
          'Unable to upload or analyze the research paper.',
      )
    }
  }

  return (
    <div>
      <header>
        <h1>FakeResearchDetector</h1>
        <p>
          Evidence-Grounded Claim Verification System for Research Integrity
        </p>
      </header>

      <UploadPage onUpload={handleUpload} />

      {selectedFile && (
        <p>
          Selected file: <strong>{selectedFile.name}</strong>
        </p>
      )}

      <UploadStatus
        status={status}
        message={message}
      />

      {analysisResult && (
        <section>
          <h2>Analysis Status</h2>

          <p>
            Paper ID:{' '}
            <strong>{analysisResult.paper_id}</strong>
          </p>

          <p>
            Status:{' '}
            <strong>{analysisResult.status}</strong>
          </p>

          <p>
            {analysisResult.message}
          </p>
        </section>
      )}
    </div>
  )
}

export default App
