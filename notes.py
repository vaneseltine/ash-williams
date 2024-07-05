from xdg import BaseDirectory, Mime

for path in [
    "pyproject.toml",
    "test/vault/Weeden_2023_Crisis.pdf",
    "10.3389.fcvm.2021.745758.pdf",
]:
    print(path, Mime.get_type2(path))

print(BaseDirectory.save_data_path("ash"))
