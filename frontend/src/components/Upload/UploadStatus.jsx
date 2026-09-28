function UploadStatus({ status, message }) {
  if (status === 'idle') {
    return null
  }

  if (status === 'uploading') {
    return (
      <div role="status">
        <p>Uploading research paper...</p>
      </div>
    )
  }

  if (status === 'processing') {
    return (
      <div role="status">
        <p>Processing research paper...</p>
        <p>Please wait while the document is being analyzed.</p>
      </div>
    )
  }

  if (status === 'success') {
    return (
      <div role="status">
        <p>{message || 'Upload completed successfully.'}</p>
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div role="alert">
        <p>{message || 'Something went wrong.'}</p>
      </div>
    )
  }

  return null
}

export default UploadStatus
