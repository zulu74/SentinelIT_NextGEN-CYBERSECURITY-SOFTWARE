
import os

def run_pluginloader():
    print("[PLUGINLOADER] Scanning plugin directory...")
    plugin_dir = "plugins"
    if not os.path.exists(plugin_dir):
        os.makedirs(plugin_dir)

    plugins = os.listdir(plugin_dir)
    if not plugins:
        print("[PLUGINLOADER] No plugins found.")
    else:
        for plugin in plugins:
            print(f"[PLUGINLOADER] Loaded plugin: {plugin}") 