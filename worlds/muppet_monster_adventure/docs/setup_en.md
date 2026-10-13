# Muppet Monster Adventure setup guide

[Game Page] | Setup | [Items] | [Locations]

[Game Page]: en_Muppet%20Monster%20Adventure
[Items]: items_en
[Locations]: locations_en

### Required Software

Important: At this time, Mac is not supported, since I do not have access to a device to test.
Want to help with testing for Mac support? Feel free to reach out!

- This has only be developed to work with the following emulators:
  - [Bizhawk](https://tasvideos.org/BizHawk/ReleaseHistory) - Tested on versions 2.10 and 2.11; with less recent versions of Archipelago, you may need less recent versions.
- [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases) version 0.6.8 or later.
- The [Muppet Monster Adventure .apworld](https://github.com/heatblayze/ArchipelagoMuppetMonsterAdventure/releases).
- A legal US Muppet Monster Adventure ROM (Serial code: SLUS-01238).  We cannot help with this step.
- A PAL or alternate NTSC version of Muppet Monster Adventure may be supported in the future.

### Create a Config (.yaml) File

#### What is a config file and why do I need one?

See the guide on setting up a basic YAML at the Archipelago setup guide: [Basic Multiworld Setup Guide](https://archipelago.gg/tutorial/Archipelago/setup_en)

This also includes instructions on generating and hosting the file.  The "On your local installation" instructions
are particularly important.

#### Where do I get a config file?

Run `ArchipelagoLauncher.exe`.  You can run Generate Template Options, copy `Muppet Monster Adventure.yaml`, fill it out, and place
it in the `players` folder. On newer versions of Archipelago, you can choose Options Creator for a more visual
approach.

### Generate and host your world

Run `ArchipelagoGenerate.exe` (or select Generate from the launcher) to build a world from the YAML files in your `players` folder.  This places
a `.zip` file in the `output` folder.

You may upload this to [the Archipelago website](https://archipelago.gg/uploads) or host the game locally with
`ArchipelagoHost.exe`. It's generally recommended to use the website.

### Setting Up Muppet Monster Adventure for Archipelago

Please follow the options below corresponding to your choice of emulator.

#### For BizHawk:

1. Download Muppet Monster Adventure.apworld from the GitHub page linked above.
2. Double click the apworld to install to your Archipelago installation.
4. Open Bizhawk and load into Muppet Monster Adventure.
5. Under Config > Customize, check the "Run in background" option to prevent disconnecting from the client while you're tabbed out of the emulator.
6. Under Config > Preferred Cores > PSX, select NymaShock.
7. Within the Archipelago Launcher, select BizHawk Client.
8. In EmuHawk, go to Tools > Lua Console. This window must stay open while playing.
9. In the Lua Console window, go to Script > Open Script.
10. Navigate to your Archipelago install folder and open data/lua/connector_bizhawk_generic.lua. The emulator and client will eventually connect to each other. The BizHawk Client window should indicate that it connected and recognized Muppet Monster Adventure.
11. To connect the client to the server, enter your room's address and port (e.g. archipelago.gg:38281) into the top text field of the client and click Connect.
12. Enter your slot name when prompted.
13. Start a new game (or if continuing an existing seed, load into that save file).
14. Start playing!

### Optional Setup

No [Poptracker](https://poptracker.github.io) package is planned or supported at this time.

[Universal Tracker](https://github.com/FarisTheAncient/Archipelago/releases) is also not supported at this.
