const fs = require('fs');
const path = require('path');
const { version } = require('./package.json');
const GitHub = require('@electron-forge/publisher-github').default;

const skipSign = !!process.argv.find((arg) => arg.startsWith('--nosign'));

class CustomGitHubPublisher extends GitHub {
  async publish(options) {
    // Modify the artifacts to include the renamed file
    for (let result of options.makeResults) {
      for (let i = 0; i < result.artifacts.length; i++) {
        if (result.artifacts[i].endsWith('AIConsole.dmg')) {
          result.artifacts[i] = path.join(
            path.dirname(result.artifacts[i]),
            `AIConsole-${version}-${result.arch}.dmg`
          );
        }
      }
    }

    // Modify the release data to create a pre-release
    options.release = {
      ...options.release,
      prerelease: true,
      draft: false,
    };

    // Call the original publish method
    return super.publish(options);
  }
}

module.exports = {
  packagerConfig: {
    executableName: process.platform === 'darwin' ? 'AIConsole' : 'aiconsole',
    asar: true,
    icon: './assets/icon',
    extraResource: ['python'],
    osxSign: {},
    ...(skipSign
      ? {}
      : {
          osxNotarize: {
            tool: 'notarytool',
            appleId: process.env.APPLE_ID,
            appleIdPassword: process.env.APPLE_ID_PASSWORD,
            teamId: process.env.APPLE_TEAM_ID,
          },
        }),
  },
  rebuildConfig: {},
  makers: [
    {
      name: '@electron-forge/maker-squirrel',
      config: {
        name: 'AIConsole',
        authors: '10Clouds',
        // An URL to an ICO file to use as the application icon (displayed in Control Panel > Programs and Features).
        iconUrl: 'https://url/to/icon.ico',
        loadingGif: './assets/blank.gif',
        // The ICO file to use as the icon for the generated Setup.exe
        setupIcon: './assets/installer-icon.ico',
      },
    },
    {
      name: '@electron-forge/maker-zip',
      config: {
        icon: './assets/icon.png',
        name: 'AIConsole',
        options: {},
      },
    },
    {
      name: '@electron-forge/maker-deb',
      config: {
        options: {
          icon: './assets/installer-icon.png',
          name: 'AIConsole',
        },
      },
    },
    {
      name: '@electron-forge/maker-rpm',
      config: {
        options: {
          icon: './assets/installer-icon.png',
          name: 'AIConsole',
        },
      },
    },
    {
      name: '@electron-forge/maker-dmg',
      config: {
        icon: './assets/installer-icon.icns',
        name: 'AIConsole',
      },
    },
  ],
  hooks: {
    postMake: async (forgeConfig, results) => {
      const { version } = require('./package.json');
      const path = require('path');
      const fs = require('fs');

      for (let result of results) {
        for (let artifact of result.artifacts) {
          if (artifact.endsWith('AIConsole.dmg')) {
            const dmgPath = artifact;
            const dmgPathWithVersionAndArch = path.join(
              path.dirname(artifact),
              `AIConsole-${version}-${result.arch}.dmg`
            );
            await fs.promises.rename(dmgPath, dmgPathWithVersionAndArch);
          }
        }
      }
    },
  },
  publishers: [
    new CustomGitHubPublisher({
      repository: {
        owner: '10clouds',
        name: 'aiconsole',
      },
      prerelease: true,
      draft: false,
    }),
  ],
  plugins: [
    {
      name: '@electron-forge/plugin-auto-unpack-natives',
      config: {},
    },
    {
      name: '@electron-forge/plugin-vite',
      config: {
        build: [
          {
            entry: './src/main.ts',
            config: 'vite.main.config.ts',
          },
          {
            entry: './src/preload.ts',
            config: 'vite.preload.config.ts',
          },
          {
            entry: './src/loader.html',
          },
        ],
        renderer: [
          {
            name: 'main_window',
            config: 'vite.renderer.config.ts',
          },
        ],
      },
    },
  ],
};
