import { Link } from 'react-router-dom'
import { APP_NAME } from '@/config.js'
import LegalPage from './LegalPage.jsx'

export default function TermsPage() {
  return (
    <LegalPage
      title="Terms of Use"
      intro={`By using ${APP_NAME} you agree to the friendly ground rules below. If something here is unclear, please ask before you rely on it.`}
    >
      <h2>For learning only</h2>
      <p>
        The material on this site is provided for educational and interview-preparation purposes only. It is a study
        aid, not professional, legal or career advice.
      </p>

      <h2>Provided as-is</h2>
      <p>
        Content is provided “as is”. We work to keep it clear and correct, but we cannot promise that it is complete,
        error-free or up to date. Technology changes quickly, so please double-check important details against
        official documentation.
      </p>
      <p>
        Using this site does not guarantee a job, an interview result, an exam result or any other career outcome.
      </p>

      <h2>Please do not copy or resell</h2>
      <p>
        Without written permission, you must not reproduce, republish, redistribute or use the original content of
        this site commercially. That includes the website code, written lessons, diagrams and branding. You are
        welcome to study from the site and to link to it. For anything beyond that, see the{' '}
        <Link to="/copyright">Copyright Notice</Link> for how to ask.
      </p>

      <h2>Your responsibility</h2>
      <p>
        You remain responsible for how you use the learning material, including any code you write, run or share
        after studying it, and for any decisions you make because of it.
      </p>

      <h2>Changes</h2>
      <p>
        These terms may be updated from time to time. The “Last updated” date above shows when they last changed.
        This page is a plain-language summary and is not legal advice.
      </p>
    </LegalPage>
  )
}
