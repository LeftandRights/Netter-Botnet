import os


def collect_files(source_folder):
    data_args = []
    for root, _, files in os.walk(source_folder):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, source_folder)
            data_args.append(f'"{full_path};{source_folder}/{relative_path}"')

    return " ".join(data_args)


folder = "core/commands"
add_data_args = collect_files(folder)

# Run PyInstaller command
os.system(f"pyinstaller --noupx --onedir {add_data_args} client.py")
