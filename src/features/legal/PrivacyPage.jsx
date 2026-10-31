import { APP_NAME } from '@/config.js'
import LegalPage from './LegalPage.jsx'

export default function PrivacyPage() {
  return (
    <LegalPage
      title="Privacy Policy"
      intro={`${APP_NAME} is built to be simple and private. This page explains, in plain language, what the site does and does not do with your information.`}
    >
      <h2>No account needed</h2>
      <p>
        You do not need to sign up, log in or give us any personal details to use {APP_NAME}. There are no forms on the
        site that collect information about you.
      </p>

      <h2>What is saved on your device</h2>
      <p>To make the site useful between visits, it saves a few things in your browser using local storage:</p>
      <ul>
        <li>your study progress, such as which topics you have marked as started or done</li>
        <li>your theme preference (light or dark)</li>
        <li>your answers to the practice quizzes</li>
      </ul>
      <p>
        This data is stored <strong>only in your browser</strong>. It is not sent to, and not stored on, this website’s
        servers. That also means it stays on the device and browser you used: it will not follow you to another
        browser or computer.
      </p>

      <h2>What we do not do</h2>
      <ul>
        <li>We do not use analytics tools.</li>
        <li>We do not use advertising trackers.</li>
        <li>We do not sell personal data.</li>
      </ul>

      <h2>Clearing your saved data</h2>
      <p>
        You are in control. You can remove the saved progress, theme and quiz answers at any time by clearing this
        site’s data in your browser settings (look for “site data”, “cookies and site data” or “local storage”).
        Clearing it resets the site to a fresh start.
      </p>

      <h2>Changes to this policy</h2>
      <p>
        If the site changes in a way that affects this page, the “Last updated” date above will change too. This page
        describes how the site works; it is not legal advice.
      </p>
    </LegalPage>
  )
}
