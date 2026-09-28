import FileUpload from '../components/Upload/FileUpload'

function UploadPage({ onUpload }) {
  return (
    <main>
      <FileUpload onUpload={onUpload} />
    </main>
  )
}

export default UploadPage
