/**
 * Windows Terminal Configuration Parser
 * Bu dosya Windows Terminal settings.json formatını parse eder ve web terminal'e uyarlar
 */

class WindowsTerminalConfig {
    constructor() {
        this.defaultConfig = this.getDefaultConfig();
        this.currentConfig = null;
    }

    /**
     * Default Windows Terminal benzeri konfigürasyon
     */
    getDefaultConfig() {
        return {
            "$help": "https://aka.ms/terminal-documentation",
            "$schema": "https://aka.ms/terminal-profiles-schema",
            "defaultProfile": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",
            "copyOnSelect": false,
            "copyFormatting": "none",
            "profiles": {
                "defaults": {
                    "fontFace": "Cascadia Code",
                    "fontSize": 14,
                    "fontWeight": "normal",
                    "cursorShape": "bar",
                    "cursorColor": "#FFFFFF",
                    "antialiasingMode": "grayscale",
                    "closeOnExit": "graceful",
                    "colorScheme": "Campbell",
                    "commandline": "powershell.exe",
                    "historySize": 9001,
                    "padding": "8, 8, 8, 8",
                    "snapOnInput": true,
                    "startingDirectory": "%USERPROFILE%",
                    "useAcrylic": false
                },
                "list": [
                    {
                        "guid": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",
                        "name": "Windows PowerShell",
                        "commandline": "powershell.exe",
                        "hidden": false,
                        "colorScheme": "Campbell",
                        "icon": "ms-appx:///ProfileIcons/{61c54bbd-c2c6-5271-96e7-009a87ff44bf}.png",
                        "tabTitle": "PowerShell"
                    },
                    {
                        "guid": "{0caa0dad-35be-5f56-a8ff-afceeeaa6101}",
                        "name": "Command Prompt",
                        "commandline": "cmd.exe",
                        "hidden": false,
                        "colorScheme": "Campbell",
                        "icon": "ms-appx:///ProfileIcons/{0caa0dad-35be-5f56-a8ff-afceeeaa6101}.png"
                    },
                    {
                        "guid": "{2c4de342-38b7-51cf-b940-2309a097f518}",
                        "name": "Ubuntu",
                        "source": "Windows.Terminal.Wsl",
                        "colorScheme": "One Half Dark",
                        "icon": "ms-appx:///ProfileIcons/linux.png"
                    },
                    {
                        "guid": "{b453ae62-4e3d-5e58-b989-0a998ec441b8}",
                        "name": "Azure Cloud Shell",
                        "source": "Windows.Terminal.Azure",
                        "colorScheme": "Vintage"
                    }
                ]
            },
            "schemes": [
                {
                    "name": "Campbell",
                    "cursorColor": "#FFFFFF",
                    "selectionBackground": "#FFFFFF",
                    "background": "#0C0C0C",
                    "foreground": "#CCCCCC",
                    "black": "#0C0C0C",
                    "blue": "#0037DA",
                    "cyan": "#3A96DD",
                    "green": "#13A10E",
                    "purple": "#881798",
                    "red": "#C50F1F",
                    "white": "#CCCCCC",
                    "yellow": "#C19C00",
                    "brightBlack": "#767676",
                    "brightBlue": "#3B78FF",
                    "brightCyan": "#61D6D6",
                    "brightGreen": "#16C60C",
                    "brightPurple": "#B4009E",
                    "brightRed": "#E74856",
                    "brightWhite": "#F2F2F2",
                    "brightYellow": "#F9F1A5"
                },
                {
                    "name": "One Half Dark",
                    "black": "#282C34",
                    "red": "#E06C75",
                    "green": "#98C379",
                    "yellow": "#E5C07B",
                    "blue": "#61AFEF",
                    "purple": "#C678DD",
                    "cyan": "#56B6C2",
                    "white": "#DCDFE4",
                    "brightBlack": "#5A6374",
                    "brightRed": "#E06C75",
                    "brightGreen": "#98C379",
                    "brightYellow": "#E5C07B",
                    "brightBlue": "#61AFEF",
                    "brightPurple": "#C678DD",
                    "brightCyan": "#56B6C2",
                    "brightWhite": "#DCDFE4",
                    "background": "#282C34",
                    "foreground": "#DCDFE4",
                    "cursorColor": "#FFFFFF",
                    "selectionBackground": "#FFFFFF"
                },
                {
                    "name": "Vintage",
                    "background": "#000000",
                    "foreground": "#C0C0C0",
                    "black": "#000000",
                    "blue": "#000080",
                    "cyan": "#008080",
                    "green": "#008000",
                    "purple": "#800080",
                    "red": "#800000",
                    "white": "#C0C0C0",
                    "yellow": "#808000",
                    "brightBlack": "#808080",
                    "brightBlue": "#0000FF",
                    "brightCyan": "#00FFFF",
                    "brightGreen": "#00FF00",
                    "brightPurple": "#FF00FF",
                    "brightRed": "#FF0000",
                    "brightWhite": "#FFFFFF",
                    "brightYellow": "#FFFF00",
                    "cursorColor": "#FFFFFF",
                    "selectionBackground": "#FFFFFF"
                }
            ],
            "actions": [
                {
                    "command": {
                        "action": "copy",
                        "singleLine": false
                    },
                    "keys": "ctrl+c"
                },
                {
                    "command": "paste",
                    "keys": "ctrl+v"
                },
                {
                    "command": "find",
                    "keys": "ctrl+shift+f"
                },
                {
                    "command": {
                        "action": "splitPane",
                        "split": "auto",
                        "splitMode": "duplicate"
                    },
                    "keys": "alt+shift+d"
                },
                {
                    "command": "newTab",
                    "keys": "ctrl+shift+t"
                },
                {
                    "command": "closeTab",
                    "keys": "ctrl+shift+w"
                },
                {
                    "command": {
                        "action": "moveFocus",
                        "direction": "down"
                    },
                    "keys": "alt+down"
                },
                {
                    "command": {
                        "action": "moveFocus",
                        "direction": "left"
                    },
                    "keys": "alt+left"
                },
                {
                    "command": {
                        "action": "moveFocus",
                        "direction": "right"
                    },
                    "keys": "alt+right"
                },
                {
                    "command": {
                        "action": "moveFocus",
                        "direction": "up"
                    },
                    "keys": "alt+up"
                }
            ]
        };
    }

    /**
     * Windows Terminal settings.json dosyasını parse et
     */
    parseConfig(jsonString) {
        try {
            const config = JSON.parse(jsonString);
            this.currentConfig = this.validateAndNormalizeConfig(config);
            return this.currentConfig;
        } catch (error) {
            console.error('Config parse error:', error);
            throw new Error('Invalid JSON configuration');
        }
    }

    /**
     * Konfigürasyonu doğrula ve normalize et
     */
    validateAndNormalizeConfig(config) {
        const normalized = { ...this.defaultConfig };

        // Profiles merge
        if (config.profiles) {
            if (config.profiles.defaults) {
                normalized.profiles.defaults = { ...normalized.profiles.defaults, ...config.profiles.defaults };
            }
            if (config.profiles.list) {
                normalized.profiles.list = config.profiles.list.map(profile => ({
                    ...normalized.profiles.defaults,
                    ...profile
                }));
            }
        }

        // Color schemes merge
        if (config.schemes) {
            normalized.schemes = [...normalized.schemes, ...config.schemes];
        }

        // Actions merge
        if (config.actions) {
            normalized.actions = [...normalized.actions, ...config.actions];
        }

        // Global settings
        if (config.defaultProfile) normalized.defaultProfile = config.defaultProfile;
        if (config.copyOnSelect !== undefined) normalized.copyOnSelect = config.copyOnSelect;
        if (config.copyFormatting) normalized.copyFormatting = config.copyFormatting;

        return normalized;
    }

    /**
     * Pegasus Terminal formatına dönüştür
     */
    convertToPegasusFormat() {
        if (!this.currentConfig) {
            this.currentConfig = this.defaultConfig;
        }

        const pegasusProfiles = {};
        const pegasusSchemes = {};

        // Color schemes'leri dönüştür
        this.currentConfig.schemes.forEach(scheme => {
            pegasusSchemes[scheme.name.toLowerCase().replace(/\s+/g, '_')] = {
                name: scheme.name,
                background: scheme.background,
                foreground: scheme.foreground,
                cursorColor: scheme.cursorColor,
                selectionBackground: scheme.selectionBackground,
                colors: {
                    black: scheme.black,
                    red: scheme.red,
                    green: scheme.green,
                    yellow: scheme.yellow,
                    blue: scheme.blue,
                    purple: scheme.purple,
                    cyan: scheme.cyan,
                    white: scheme.white,
                    brightBlack: scheme.brightBlack,
                    brightRed: scheme.brightRed,
                    brightGreen: scheme.brightGreen,
                    brightYellow: scheme.brightYellow,
                    brightBlue: scheme.brightBlue,
                    brightPurple: scheme.brightPurple,
                    brightCyan: scheme.brightCyan,
                    brightWhite: scheme.brightWhite
                }
            };
        });

        // Profiles'ları dönüştür
        this.currentConfig.profiles.list.forEach(profile => {
            const scheme = this.currentConfig.schemes.find(s => s.name === profile.colorScheme) || this.currentConfig.schemes[0];
            const profileKey = profile.name.toLowerCase().replace(/\s+/g, '_');

            pegasusProfiles[profileKey] = {
                name: profile.name,
                guid: profile.guid,
                icon: this.getProfileIcon(profile),
                prompt: this.getProfilePrompt(profile),
                background: scheme.background,
                foreground: scheme.foreground,
                cursorColor: scheme.cursorColor,
                fontFamily: profile.fontFace || this.currentConfig.profiles.defaults.fontFace,
                fontSize: profile.fontSize || this.currentConfig.profiles.defaults.fontSize,
                commandline: profile.commandline,
                startingDirectory: profile.startingDirectory,
                colorScheme: profile.colorScheme,
                hidden: profile.hidden || false
            };
        });

        return {
            profiles: pegasusProfiles,
            schemes: pegasusSchemes,
            settings: {
                defaultProfile: this.currentConfig.defaultProfile,
                copyOnSelect: this.currentConfig.copyOnSelect,
                copyFormatting: this.currentConfig.copyFormatting
            },
            actions: this.currentConfig.actions
        };
    }

    /**
     * Profile için ikon belirle
     */
    getProfileIcon(profile) {
        if (profile.name.toLowerCase().includes('powershell')) return '🔷';
        if (profile.name.toLowerCase().includes('cmd') || profile.name.toLowerCase().includes('command')) return '⚫';
        if (profile.name.toLowerCase().includes('ubuntu') || profile.name.toLowerCase().includes('linux')) return '🐧';
        if (profile.name.toLowerCase().includes('azure')) return '☁️';
        if (profile.name.toLowerCase().includes('git')) return '🌿';
        return '💻';
    }

    /**
     * Profile için prompt belirle
     */
    getProfilePrompt(profile) {
        if (profile.name.toLowerCase().includes('powershell')) return 'PS>';
        if (profile.name.toLowerCase().includes('cmd') || profile.name.toLowerCase().includes('command')) return 'C:\\>';
        if (profile.name.toLowerCase().includes('ubuntu') || profile.name.toLowerCase().includes('linux')) return '$';
        return '$';
    }

    /**
     * Konfigürasyonu JSON olarak export et
     */
    exportConfig() {
        return JSON.stringify(this.currentConfig || this.defaultConfig, null, 2);
    }

    /**
     * Konfigürasyonu dosyadan yükle
     */
    async loadFromFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const config = this.parseConfig(e.target.result);
                    resolve(config);
                } catch (error) {
                    reject(error);
                }
            };
            reader.onerror = () => reject(new Error('File read error'));
            reader.readAsText(file);
        });
    }

    /**
     * Konfigürasyonu dosya olarak indir
     */
    downloadConfig(filename = 'pegasus-terminal-settings.json') {
        const config = this.exportConfig();
        const blob = new Blob([config], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }

    /**
     * Yeni profil ekle
     */
    addProfile(profile) {
        if (!this.currentConfig) {
            this.currentConfig = { ...this.defaultConfig };
        }

        const newProfile = {
            guid: this.generateGuid(),
            name: profile.name,
            commandline: profile.commandline || 'cmd.exe',
            colorScheme: profile.colorScheme || 'Campbell',
            fontFace: profile.fontFace || 'Cascadia Code',
            fontSize: profile.fontSize || 14,
            hidden: false,
            ...profile
        };

        this.currentConfig.profiles.list.push(newProfile);
        return newProfile;
    }

    /**
     * Yeni color scheme ekle
     */
    addColorScheme(scheme) {
        if (!this.currentConfig) {
            this.currentConfig = { ...this.defaultConfig };
        }

        this.currentConfig.schemes.push(scheme);
        return scheme;
    }

    /**
     * GUID oluştur
     */
    generateGuid() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            const r = Math.random() * 16 | 0;
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    /**
     * Keybinding'leri parse et
     */
    parseKeybindings() {
        if (!this.currentConfig || !this.currentConfig.actions) {
            return [];
        }

        return this.currentConfig.actions.map(action => ({
            keys: action.keys,
            command: action.command,
            description: this.getActionDescription(action.command)
        }));
    }

    /**
     * Action açıklaması al
     */
    getActionDescription(command) {
        if (typeof command === 'string') {
            return command;
        }

        if (command.action) {
            switch (command.action) {
                case 'copy': return 'Copy text';
                case 'paste': return 'Paste text';
                case 'splitPane': return 'Split pane';
                case 'newTab': return 'New tab';
                case 'closeTab': return 'Close tab';
                case 'moveFocus': return `Move focus ${command.direction}`;
                default: return command.action;
            }
        }

        return 'Unknown action';
    }
}

// Global instance
window.WindowsTerminalConfig = WindowsTerminalConfig;
