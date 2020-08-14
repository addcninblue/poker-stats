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
      example = defaultDomain;
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
      # This is an one-shot systemd service to make sure that the
      # required network is there.
      systemd.services.init-pokernow-stats-network-and-files = {
        description = "Create the network bridge ${bridgeNetworkName} for pokernow-stats.";
        after = [ "network.target" ];
        wantedBy = [ "multi-user.target" ];

        serviceConfig.Type = "oneshot";

        script = let dockercli = "${config.virtualisation.docker.package}/bin/docker";
        in ''
                   # Put a true at the end to prevent getting non-zero return code, which will
                   # crash the whole service.
                   check=$(${dockercli} network ls | grep "${bridgeNetworkName}" || true)
                   if [ -z "$check" ]; then
                     ${dockercli} network create ${bridgeNetworkName}
                   else
                     echo "${bridgeNetworkName} already exists in docker"
                   fi
        '';
      };

      services.nginx.virtualHosts."${cfg.domain}" = {
      enableACME = true;
      forceSSL = true;
      locations."/" = {
        proxyPass = "http://localhost:${toString cfg.port}";
        extraConfig =
          # required when the target is also TLS server with multiple hosts
          "proxy_ssl_server_name on;" +
          # required when the server wants to use HTTP Authentication
          "proxy_pass_header Authorization;"
          ;
        };
      };
    }
  );
}
