# Token Generation Utility

This utility helps generate authentication tokens for Intuit API calls. It simplifies the setup process and handles SSO authentication.

## Setup (Mac OS)

1. **Run the setup script**

   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   This will:
   - Check your Python installation (requires Python 3.7+)
   - Set up a virtual environment
   - Install required dependencies
   - Create a `.env` file template

2. **Configure your credentials**

   Edit the `.env` file with your Intuit credentials:
   ```
   CORP_ID=your_corp_id_here
   EMAIL=your_email_here
   APP_SECRET=your_app_secret_here
   ```

## Usage

1. **Run the utility**

   ```bash
   ./run.sh
   ```

   This script will:
   - Activate the virtual environment
   - Run the TokenGeneration script
   - Guide you through the SSO authentication process
   - Test the authentication by making a sample API call
   - Display the generated headers for use in your applications

2. **SSO Authentication**

   During the authentication process, you'll need to:
   - Watch for the URL that appears in the terminal
   - Copy and paste this URL into your browser
   - Complete the Intuit SSO login process
   - Return to the terminal to see the generated headers

## Troubleshooting

- **Missing Dependencies**: If you encounter errors about missing Python modules, run `./setup.sh` again
- **Authentication Failed**: Verify your CORP_ID and EMAIL in the `.env` file
- **SSO Problems**: Ensure you're correctly following the browser authentication flow

## Files

- `setup.sh`: Environment setup script
- `run.sh`: Script to run the token generation utility
- `TokenGeneration_env.py`: Main Python script that handles authentication
- `.env`: Configuration file for your credentials (created from `.env.example`)
- `requirements.txt`: Python dependencies
