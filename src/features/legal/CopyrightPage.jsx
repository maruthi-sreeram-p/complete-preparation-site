import { Link } from 'react-router-dom'
import { CONTACT_EMAIL, SITE_OWNER_NAME } from '@/config.js'
import LegalPage from './LegalPage.jsx'

export default function CopyrightPage() {
  return (
    <LegalPage title="Copyright Notice" showDate={false}>
      <p>
        <strong>© 2026 {SITE_OWNER_NAME}. All rights reserved.</strong>
      </p>

      <h2>What is protected</h2>
      <p>The following original works on this website are protected by copyright:</p>
      <ul>
        <li>the website’s code</li>
        <li>the written lessons</li>
        <li>the original diagrams</li>
        <li>the branding, including the name, logo and wordmark</li>
      </ul>

      <h2>Permission requests and copyright concerns</h2>
      <p>
        If you would like permission to use any of this material, or you have a copyright concern, please get in
        touch at <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>. Please tell us which page you mean and what you would like to do.
      </p>

      <p>
        Names of third-party technologies mentioned in the lessons belong to their respective owners. See also the{' '}
        <Link to="/terms">Terms of Use</Link>.
      </p>
    </LegalPage>
  )
}
