{ config, pkgs, lib, ... }:

let cfg = config.server.pokernow-stats;
defaultPort = 10003;
defaultDomain = "pokernow-stats.addcnin.blue";

in {
  options.server.pokernow-stats = {
    enable = lib.mkEnableOption "Enable the pokernow stats service.";
    workDir = lib.mkOption {
      type = lib.types.str;
      description = ''
      '';
      default = "/mnt/pokernow-stats";
      example = "/mnt/pokernow-stats";
    };
    port = lib.mkOption {
      type = lib.types.port;
      description = "";
      default = defaultPort;
    };
    domain = lib.mkOption {
      type = lib.types.str;
      description = "The domain to configure nginx for this service.";
      default = defaultDomain;
      exmple = defaultDomain;
    };
  };

  config = lib.mkIf cfg.enable (
    let bridgeNetworkName = "pokernow-stats_network";

        runner = {
          user = "pokernow-stats";
          group = "pokernow-stats";
        };
    in {
      docker-containers."pokernow-stats" = {
        image = "pokernow-stats:0.1";
        ports = [ "${toString cfg.port}:8000" ];
        extraDockerOptions = [ "--network=${bridgeNetworkName}" ];
      };
    };
  );
}
