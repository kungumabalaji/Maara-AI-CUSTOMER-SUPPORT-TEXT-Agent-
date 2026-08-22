interface LogoProps {
  size?: number
  withWordmark?: boolean
}

export default function Logo({ size = 34, withWordmark = true }: LogoProps) {
  return (
    <div className="logo-lockup">
      <img src="/maara-logo.png" alt="MAARA" className="logo-mark" style={{ width: size, height: size }} />
      {withWordmark && (
        <div className="logo-text">
          <strong>MAARA</strong>
          <span>SUPPORT</span>
        </div>
      )}
    </div>
  )
}
