/**
 * Purges jsDelivr cache for all theme files in the repository
 * This script handles the asynchronous purge operation and status polling
 */

const https = require("https");
const fs = require("fs");
const path = require("path");

const PURGE_API_URL = "https://purge.jsdelivr.net/";
const STATUS_CHECK_INTERVAL = 1000; // 1 second
const MAX_STATUS_CHECKS = 60; // Maximum 60 seconds wait

/**
 * Makes an HTTPS POST request
 */
function httpsPost(url, data) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const postData = JSON.stringify(data);

    const options = {
      hostname: urlObj.hostname,
      port: 443,
      path: urlObj.pathname,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(postData),
      },
    };

    const req = https.request(options, (res) => {
      let body = "";
      res.on("data", (chunk) => (body += chunk));
      res.on("end", () => {
        try {
          resolve(JSON.parse(body));
        } catch (e) {
          reject(new Error(`Failed to parse response: ${body}`));
        }
      });
    });

    req.on("error", reject);
    req.write(postData);
    req.end();
  });
}

/**
 * Makes an HTTPS GET request
 */
function httpsGet(url) {
  return new Promise((resolve, reject) => {
    https
      .get(url, (res) => {
        let body = "";
        res.on("data", (chunk) => (body += chunk));
        res.on("end", () => {
          try {
            resolve(JSON.parse(body));
          } catch (e) {
            reject(new Error(`Failed to parse response: ${body}`));
          }
        });
      })
      .on("error", reject);
  });
}

/**
 * Polls the purge status until completion
 */
async function waitForPurgeCompletion(purgeId) {
  let checks = 0;

  while (checks < MAX_STATUS_CHECKS) {
    await new Promise((resolve) => setTimeout(resolve, STATUS_CHECK_INTERVAL));

    const statusUrl = `${PURGE_API_URL}status/${purgeId}`;
    console.log(
      `Checking purge status (attempt ${checks + 1}/${MAX_STATUS_CHECKS})...`
    );

    const status = await httpsGet(statusUrl);
    console.log(`Status: ${status.status}`);

    if (status.status === "finished") {
      return status;
    } else if (status.status === "failed") {
      throw new Error("Purge operation failed");
    }

    checks++;
  }

  throw new Error("Purge operation timed out");
}

/**
 * Dynamically discovers theme directories by scanning for folders containing theme.css
 */
function discoverThemes() {
  const rootDir = path.resolve(__dirname, "../..");
  const themes = [];

  try {
    const entries = fs.readdirSync(rootDir, { withFileTypes: true });

    for (const entry of entries) {
      if (entry.isDirectory() && !entry.name.startsWith(".")) {
        const themeCssPath = path.join(rootDir, entry.name, "theme.css");
        if (fs.existsSync(themeCssPath)) {
          themes.push(entry.name);
        }
      }
    }
  } catch (error) {
    throw new Error(`Failed to discover themes: ${error.message}`);
  }

  return themes;
}

/**
 * Main function to purge jsDelivr cache
 */
async function main() {
  const repository = process.env.GITHUB_REPOSITORY;
  const version = process.env.GITHUB_REF_NAME;

  if (!repository || !version) {
    console.error("Error: GITHUB_REPOSITORY and GITHUB_REF_NAME must be set");
    process.exit(1);
  }

  console.log(`Repository: ${repository}`);
  console.log(`Version: ${version}`);

  // Dynamically discover themes by scanning for directories with theme.css
  const themes = discoverThemes();
  console.log(`\nDiscovered themes: ${themes.join(", ")}`);

  if (themes.length === 0) {
    console.error("Error: No themes found");
    process.exit(1);
  }

  // Build the list of paths to purge
  const paths = [];

  for (const theme of themes) {
    // Purge specific version
    paths.push(`/gh/${repository}@${version}/${theme}/theme.css`);

    // Purge latest tag (if this is a release)
    paths.push(`/gh/${repository}@latest/${theme}/theme.css`);

    // Purge without version tag (uses default branch)
    paths.push(`/gh/${repository}/${theme}/theme.css`);
  }

  console.log("\nPaths to purge:");
  paths.forEach((path) => console.log(`  ${path}`));
  console.log("");

  // Make the purge request
  console.log("Sending purge request...");
  const purgeResponse = await httpsPost(PURGE_API_URL, { path: paths });

  console.log(`Purge initiated with ID: ${purgeResponse.id}`);
  console.log(`Initial status: ${purgeResponse.status}`);

  // Wait for completion
  console.log("\nWaiting for purge to complete...");
  const finalStatus = await waitForPurgeCompletion(purgeResponse.id);

  console.log("\n✅ Purge completed successfully!");
  console.log("\nDetailed results:");
  console.log(JSON.stringify(finalStatus, null, 2));

  // Check for any throttled or failed paths
  const throttledPaths = [];
  const failedPaths = [];

  if (finalStatus.paths) {
    for (const [path, details] of Object.entries(finalStatus.paths)) {
      if (details.throttled) {
        throttledPaths.push(path);
      } else if (details.providers) {
        for (const [provider, success] of Object.entries(details.providers)) {
          if (!success) {
            failedPaths.push(`${path} (${provider})`);
          }
        }
      }
    }
  }

  if (throttledPaths.length > 0) {
    console.warn("\n⚠️  Some paths were throttled:");
    throttledPaths.forEach((path) => console.warn(`  ${path}`));
  }

  if (failedPaths.length > 0) {
    console.error("\n❌ Some paths failed to purge:");
    failedPaths.forEach((path) => console.error(`  ${path}`));
    process.exit(1);
  }
}

// Run the script
main().catch((error) => {
  console.error("\n❌ Error:", error.message);
  process.exit(1);
});
