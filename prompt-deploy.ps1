Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   FIRST HOUR - AUTOMATED DEPLOYMENT TOOL    " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will completely bypass the manual dashboards." -ForegroundColor Yellow
Write-Host "It requires the Vercel CLI to be installed." -ForegroundColor Yellow
Write-Host ""

if (!(Get-Command npx -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Node.js (npm/npx) is not installed. Please install Node.js first." -ForegroundColor Red
    exit 1
}

Write-Host "STEP 1: RENDER BACKEND (AUTOMATED BLUEPRINT)" -ForegroundColor Cyan
Write-Host "We have upgraded the repository with a unified Render Blueprint."
Write-Host "1. Push the latest code to GitHub:"
Write-Host "   git add . ; git commit -m 'Deploy config' ; git push"
Write-Host "2. Go to: https://dashboard.render.com/blueprints"
Write-Host "3. Click 'New Blueprint Instance' and connect the FIRSTHOUR repo."
Write-Host "Render will now AUTOMATICALLY build the Postgres Database, the API, and link them together."
Write-Host ""
$renderUrl = Read-Host "Once Render is deployed, paste the API URL here (e.g. https://first-hour-api.onrender.com)"

if ($renderUrl.EndsWith("/")) {
    $renderUrl = $renderUrl.Substring(0, $renderUrl.Length - 1)
}

Write-Host ""
Write-Host "STEP 2: AUTH0 CONFIGURATION" -ForegroundColor Cyan
$authDomain = Read-Host "Enter your Auth0 Domain (e.g. tenant.us.auth0.com)"
$authAudience = Read-Host "Enter your Auth0 API Audience (e.g. https://api.firsthour.com)"
$authClientId = Read-Host "Enter your Auth0 SPA Client ID"

Write-Host ""
Write-Host "STEP 3: VERCEL FRONTEND (AUTOMATED CLI DEPLOY)" -ForegroundColor Cyan
Write-Host "We will now deploy the frontend directly to Vercel."
Set-Location frontend

Write-Host "Logging into Vercel..."
npx vercel login

Write-Host "Linking project..."
npx vercel link --yes

Write-Host "Uploading Environment Variables..."
# We pipe the values into Vercel env add
"$renderUrl/api" | npx vercel env add VITE_API_BASE_URL production
"$authDomain" | npx vercel env add VITE_AUTH0_DOMAIN production
"$authClientId" | npx vercel env add VITE_AUTH0_CLIENT_ID production
"$authAudience" | npx vercel env add VITE_AUTH0_AUDIENCE production

Write-Host "Deploying to Production!"
$vercelOutput = npx vercel deploy --prod --yes
Write-Host "Deployed to: $vercelOutput" -ForegroundColor Green

Write-Host ""
Write-Host "STEP 4: FINAL CORS LINKING" -ForegroundColor Cyan
Write-Host "Your frontend is live at: $vercelOutput"
Write-Host "Go back to the Render Dashboard -> first-hour-api -> Environment"
Write-Host "Set CORS_ORIGINS = $vercelOutput"
Write-Host "Set AUTH_PROVIDER_DOMAIN = $authDomain"
Write-Host "Set AUTH_PROVIDER_AUDIENCE = $authAudience"
Write-Host "Save changes. You are completely done." -ForegroundColor Green
