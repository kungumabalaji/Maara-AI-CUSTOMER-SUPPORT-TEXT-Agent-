import type { BotConfig } from '../lib/types'
import ChatWidget from '../components/ChatWidget'

const EMBED_SNIPPET = `<script
  src="https://cdn.maara.app/support-widget.js"
  data-maara-org="your-org-id"
  async
></script>`

export default function WidgetDemoPage({ botConfig }: { botConfig: BotConfig }) {
  return (
    <div className="page-shell">
      <div className="page-heading">
        <p className="eyebrow">Widget · embeddable</p>
        <h1>Drop it on any website</h1>
        <p className="page-subtext">
          The launcher sits bottom-right on your site and opens the same {botConfig.name} chat — no login required for
          customers.
        </p>
      </div>

      <div className="panel widget-demo-panel">
        <div className="widget-demo-mock">
          <div className="mock-browser-bar">
            <span /> <span /> <span />
            <div className="mock-url">https://your-website.com</div>
          </div>
          <div className="mock-page-content">
            <p className="eyebrow">your-website.com</p>
            <h2>Welcome to your product</h2>
            <p>This area represents your existing site. The support launcher floats on top of it, untouched.</p>
          </div>
          <ChatWidget botConfig={botConfig} />
        </div>

        <div className="widget-demo-embed">
          <p className="rail-label">Embed snippet</p>
          <pre className="code-block">{EMBED_SNIPPET}</pre>
          <p className="page-subtext">Paste this once, before <code>&lt;/body&gt;</code>. Styling and content stay in sync with your admin settings.</p>
        </div>
      </div>
    </div>
  )
}
