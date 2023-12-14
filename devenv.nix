{ pkgs, ... }:

{
  packages = [
    pkgs.just
    pkgs.git
    pkgs.zig
    pkgs.cargo
    pkgs.go
    pkgs.nodejs_20
    pkgs.yarn
    pkgs.wget
    pkgs.rnix-lsp
    pkgs.zls
    pkgs.time
  ];

  enterShell = ''
    git --version
    # poetry install
  '';

  languages.go.enable = true;
  languages.zig.enable = true;

  languages.python = {
    enable = true;
    package = pkgs.python311;
    # package = pkgs.pypy310;
    poetry.enable = true;
    poetry.package = pkgs.poetry;
    venv.enable = true;
  };

}
