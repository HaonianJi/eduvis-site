export default function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-white">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
          <div className="text-gray-600">© {new Date().getFullYear()} EduVisBench / EduVisAgent Research Project</div>
          <div className="flex flex-wrap gap-6">
            <a className="text-gray-600 hover:text-gray-900 transition-colors text-sm font-medium" href="/cite">
              Citation
            </a>
            <a className="text-gray-600 hover:text-gray-900 transition-colors text-sm font-medium" href="/contact">
              Contact
            </a>
            <a
              className="text-gray-600 hover:text-gray-900 transition-colors text-sm font-medium"
              href="https://github.com/aiming-lab"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
            <a
              className="text-gray-600 hover:text-gray-900 transition-colors text-sm font-medium"
              href="https://arxiv.org/abs/2505.16832"
              target="_blank"
              rel="noopener noreferrer"
            >
              arXiv
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
