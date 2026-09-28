const MAX_FILE_SIZE = 20 * 1024 * 1024

export function validatePDF(file) {
  if (!file) {
    return {
      valid: false,
      message: 'Please select a file.',
    }
  }

  const isPDF =
    file.type === 'application/pdf' ||
    file.name.toLowerCase().endsWith('.pdf')

  if (!isPDF) {
    return {
      valid: false,
      message: 'Only PDF files are allowed.',
    }
  }

  if (file.size > MAX_FILE_SIZE) {
    return {
      valid: false,
      message: 'PDF file size must be 20 MB or less.',
    }
  }

  return {
    valid: true,
    message: '',
  }
}
