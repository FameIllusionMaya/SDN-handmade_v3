<template>
  <div class="row">
    <div class="col-sm-12 col-md-12">
      <form class="card" @submit.prevent="onSubmit" method="post">
        <div class="card-header">
          <h3 class="card-title">Route</h3>
        </div>
    <div class="card-body">
      <div class="row">
            <div class="col-md-4">
              <div class="form-group">
                <label class="form-label">Source</label>
                <select @change="onActionChange(i)" v-model="source" class="form-control">
                  <option value="0" disabled>Select source</option>
                  <option v-for="network in networks" :key="network" :value="network">{{network}}/{{ mask[networks.indexOf(network)] }}</option>
                </select>
              </div>
            </div>
      <div class="col-md-4">
              <div class="form-group">
                <label class="form-label">Destination</label>
                <select @change="onActionChange(i)" v-model="destination" class="form-control">
                  <option value="0" disabled>Select destination</option>
                  <option v-for="network in networks" :key="network" :value="network">{{ network }}/{{ mask[networks.indexOf(network)] }}</option>
                </select>
              </div>
            </div>
            <div class="col-md-4">
              <button style="margin-top:25px" type="submit" class="btn btn-primary">Ok</button>
            </div>
          </div>
      </div>
      </form>
      <div class="card">
        <div class="card-header">
          Network graph
        </div>
        <div class="card-body">
          <network-graph :nodes="graphNode" :edges="graphEdge" @click="onClick" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NetworkGraph from "@/components/NetworkGraph.vue";
import * as jsnx from "jsnetworkx";
import ipaddrMixin from "@/mixins/ipaddr";

export default {
  data() {
    return {
      devices: [],
      mode: "findpath",
      graph: null,
      node_label: "hostname",
      graphRawData: null,
      nodes_: {},
      graphNode: [],
      graphEdge: [],
      interval: null,
      eventName: "",
      information: "",
      selectEdge: ["192.168.2.0-192.168.2.1", "192.168.2.2-192.168.2.3"],
      nodeSelect: [],
      highlightNode: [],
      routes: [],
      source: "",
      destination: "",
      networks: [],
      mask:[],
      links: [],
      deviceID: "",
      addlink: [],
      addlinkmask: [],
      check: [],
      click: 0,
      network_in_link: [],
      network_in_addlink: [],
      check_use_link: {},
      neighbor: [],
      router_in_graph : [],
      link_in_graph : [],
      check_switch : [],
      edges : [],
      flow_routing : [],
      net_switch : []
    };
  },
  components: {
    NetworkGraph
  },
  mixins: [ipaddrMixin],
  async mounted(){
    await this.fetchData();
  },
  methods: {
    async onSubmit(n) {
      let check = true;
      this.click =  1;
      this.deviceID = "";
      this.addlink = [];
      this.addlinkmask = [];
      this.updateGraph();
      if(!this.check_in_flow_routing()){
        this.deviceID = this.getDeviceIDFromNetwork(this.source);
        //alert(this.deviceID);
        while (check) {
          check = this.getNextHopIP();
          //alert(this.deviceID);
        }
      }
      //this.click = 0;
    },
    async onClick(param) {
      this.eventName = "onClick"
      this.information = param
      if (this.mode == "findpath") {
        if (this.nodeSelect.length >= 2) {
          this.nodeSelect = [];
        }
        this.highlightNode = [];
        if (param.nodes.length < 1) {
          this.updateGraph();
          return;
        }
        this.nodeSelect.push(param.nodes[0]);
        // this.highlightNode = [];
        if (this.nodeSelect.length == 2) {
          const rawData = await this.$axios.$get(
            `path/${this.nodeSelect[0]},${this.nodeSelect[1]}`
          );
          this.highlightNode = rawData.paths;
        }
        this.updateGraph();
        // await this.$axios.$get("path/" + ip);
        return;
      }
      const info = param;
      if (param.nodes) {
        const ip = param.nodes[0];
        const device = await this.$axios.$get("device/ifip/" + ip);
        info["device"] = device;
      }
      this.eventName = "onClick";
      this.information = JSON.stringify(info, null, 2);
    },
    hex_to_int(hex){
      return parseInt(hex, 16);
    },
    check_switchs(hex){
      if (this.hex_to_int(hex)%2 == 0){
        return true;
      }
      else if (hex.includes("Switch") && !hex.includes("Router")){
        return true;
      }
      else{
        return false;
      }
    },
    check_in_flow_routing(){
      for (var i=0; i<this.flow_routing.length; i++){
        var src_net = this.getNetworkFromIP(this.flow_routing[i].src_ip, this.getSubnetFromWildcard(this.flow_routing[i].src_wildcard));
        var dst_net = this.getNetworkFromIP(this.flow_routing[i].dst_ip, this.getSubnetFromWildcard(this.flow_routing[i].dst_wildcard));
        if (src_net == this.source && dst_net == this.destination){
          for (var j=0; j<this.flow_routing[i].actions.length; j++){
            for (var k=0; k<this.links.length; k++){
              if (this.links[k].src_ip == this.flow_routing[i].actions[j].data || this.links[k].dst_ip == this.flow_routing[i].actions[j].data){
                var ifaces = this.findInterfaces(this.links[k].src_node_id, this.links[k].dst_node_id, this.links[k].src_ip);
                var addmask = ifaces.subnet;
                this.addlink.push(this.links[k].src_ip, this.links[k].dst_ip);
                this.addlinkmask.push(addmask, addmask);
              }
            }
          }
          return true;
        }
      }
      return false;
    },
    getNetwork() {
      for (var i = 0; i < this.routes.length; i++) {
       for (var j = 0; j < this.routes[i].length; j++) {
         if (this.networks.indexOf(this.routes[i][j].dst) < 0 && this.routes[i][j].dst != "0.0.0.0" && this.routes[i][j].mask != "255.255.255.255") {
            this.networks.push(this.routes[i][j].dst);
            this.mask.push(this.subnetToCidr(this.routes[i][j].mask));
          }
        }
      }
    },
    getDeviceIDFromNetwork(network) {
      for (var i=0; i < this.routes.length; i++) {
        for (var j=0; j < this.routes[i].length; j++) {
          if (this.routes[i][j].dst == network && this.routes[i][j].proto == 2) {
            this.deviceID = this.routes[i][j].device_id.$oid;
            if (this.check.indexOf(network) >= 0) {
              this.deviceID = this.getLink(this.routes[i][j].next_hop, this.routes[i][j].if_index);
            }
            return this.deviceID;
          }
        }
      }
    },
    getNextHopIP () {
      for (var i=0; i < this.routes.length; i++) {
        if (this.routes[i][0].device_id.$oid == this.deviceID) {
          for (var j=0; j < this.routes[i].length; j++) {
            if (this.routes[i][j].dst == "0.0.0.0" && this.routes[i][j].mask == "0.0.0.0"){
              var next_hop = this.routes[i][j].next_hop;
              var if_index = this.routes[i][j].if_index;
            }
            else if (this.routes[i][j].dst == this.getNetworkFromIP(this.destination, this.routes[i][j].mask)) {
              if (this.routes[i][j].next_hop == "0.0.0.0") {
                this.deviceID = this.getLink(this.routes[i][j].next_hop, this.routes[i][j].if_index);
                return false;
              } else {
                this.deviceID = this.getLink(this.routes[i][j].next_hop, this.routes[i][j].if_index);
                return true;
              }
            }
          }
          /*
          for (var j=0; j < this.routes[i].length; j++) {
            if (this.routes[i][j].mask == "255.255.255.255" && this.source != this.destination) {
              this.deviceID = this.getLink(this.routes[i][j].next_hop, this.routes[i][j].if_index);
              return false;
            }
          }
          */
        }
      }
      this.deviceID = this.getLink(next_hop, if_index);
      return true;
    },
    getLink (next_hop, if_index) {
      //alert(next_hop+"   "+if_index+" "+this.deviceID);
      for (var i=0; i < this.links.length; i++) {
        var ifaces = this.findInterfaces(this.links[i].src_node_id, this.links[i].dst_node_id, this.links[i].src_ip);
        var addmask = ifaces.subnet;
        //between first hop and last hop
        if (this.links[i].dst_ip == next_hop || this.links[i].src_ip == next_hop) {
          this.addlink.push(this.links[i].src_ip, this.links[i].dst_ip);
          this.addlinkmask.push(addmask, addmask);
          return this.findNodeID(this.links[i].src_node_id, this.links[i].dst_node_id, next_hop);
        }
        //first hop and last hop
        else if (((this.links[i].src_if_index == if_index && this.deviceID == this.links[i].src_node_id.$oid)||(this.links[i].dst_if_index == if_index && this.deviceID == this.links[i].dst_node_id.$oid)) && next_hop == "0.0.0.0") {
          this.addlink.push(this.links[i].src_ip, this.links[i].dst_ip);
          this.addlinkmask.push(addmask, addmask);
          for (var j=0; j < this.routes.length; j++){
            for (var k=0; k < this.routes[j].length; k++){
              if (this.links[i].src_node_id.$oid == this.routes[j][k].device_id.$oid && (this.routes[j][k].dst == this.destination || this.routes[j][k].dst == this.source)&& this.routes[j][k].next_hop == "0.0.0.0") {
                return this.links[i].src_node_id.$oid;
              }
              else if (this.links[i].dst_node_id.$oid == this.routes[j][k].device_id.$oid && (this.routes[j][k].dst == this.destination  || this.routes[j][k].dst == this.source) && this.routes[j][k].next_hop == "0.0.0.0") {
                return this.links[i].dst_node_id.$oid;
              }
            }
          }
        }
      }
    },
    getNetworkFromIP(ip, mask) {
      var check = "";
      ip = ip.split(".");
      mask = mask.split(".");
      for (var i=0; i < mask.length; i++) {
        if (mask[i] != "255") {
          ip [i] = parseInt(ip[i], 10).toString(2).padStart(8, "0");
          mask[i] = parseInt(mask[i], 10).toString(2).padStart(8, "0");
          for (var j=0; j < mask[i].length; j++){
            if (mask[i][j] == "0") {
              check += "0";
            } else {
              check += ip[i][j];
            }
          }
          ip[i] = parseInt(check, 2);
        }
      }
      return ip.join(".");
    },
    calculate_usage_percent(src_usage, dst_usage, speed) {
      return Math.max(src_usage, dst_usage) / speed * 100;
    },
    async fetchGraph() {
      this.neighbor = [];
      this.flow_routing = [];
      try {
        let res = await this.$axios.$get("device");
        this.devices = res.devices;
        res = await this.$axios.$get("link");
        this.links = res.links;
        res = await this.$axios.$get(`flow/routing`);
        this.flow_routing = res.flows;
        let res2;
        let device;
        for (var i = 0; i < this.devices.length; i++) {
          device = this.devices[i];
          res2 = await this.$axios.$get(`routes/${device._id.$oid}`);
          if (res2) {
            this.routes.push(res2.routes);
          }
        }
        for (var i = 0; i < this.devices.length; i++) {
          device = this.devices[i];
          res2 = await this.$axios.$get(`device/${device._id.$oid}/neighbor`);
          if (res2) {
            this.neighbor.push(res2.neighbor);
          }
        }
        this.getNetwork();
      } catch (e) {}
      this.form = {
        ...this.propForm
      };
      this.graphRawData = await this.$axios.$get("link");
      this.updateGraph();
    },
    count(list, check) {
      var count = 0;
      for (var i=0; i < list.length; i++) {
        if (list[i] == check) {
          count = count +1;
        }
      }
      return count;
    },
    getSubnetFromWildcard(wildcard){
      wildcard = wildcard.split(".");
      for (var i=0; i<wildcard.length; i++){
        wildcard[i] = (255 - parseInt(wildcard[i])).toString();
      }
      return wildcard.join(".");
    },
    getNetworkInLink() {
      for (var i=0; i < this.links.length; i++) {
        for (var a=0; a<this.devices.length; a++) {
          if (this.devices[a]._id.$oid == this.links[i].src_node_id.$oid || this.devices[a]._id.$oid == this.links[i].dst_node_id.$oid) {
            for (var b=0; b<this.devices[a].interfaces.length; b++) {
              if (this.links[i].src_ip == this.devices[a].interfaces[b].ipv4_address){
                this.network_in_link.push(this.getNetworkFromIP(this.links[i].src_ip, this.devices[a].interfaces[b].subnet));
              }
            }
          }
        }
      }
    },
    findInterfaces(src_node_id, dst_node_id, ip) {
      for (var a=0; a<this.devices.length; a++) {
        if (this.devices[a]._id.$oid == src_node_id.$oid || this.devices[a]._id.$oid == dst_node_id.$oid) {
          for (var b=0; b<this.devices[a].interfaces.length; b++) {
            if (ip == this.devices[a].interfaces[b].ipv4_address){
              return this.devices[a].interfaces[b];
            }
          }
        }
      }
    },
    findNodeID(src_node_id, dst_node_id, ip) {
      for (var a=0; a<this.devices.length; a++) {
        if (this.devices[a]._id.$oid == src_node_id.$oid || this.devices[a]._id.$oid == dst_node_id.$oid) {
          for (var b=0; b<this.devices[a].interfaces.length; b++) {
            if (ip == this.devices[a].interfaces[b].ipv4_address){
              return this.devices[a]._id.$oid;
            }
          }
        }
      }
    },
    getNetworkInAddlink(){
      for(var i=0; i<this.addlink.length; i++) {
        this.network_in_addlink.push(this.getNetworkFromIP(this.addlink[i], this.addlinkmask[i]));
      }
    },
    updateGraph() {
      this.network_in_link = [];
      this.network_in_addlink = [];
      this.getNetworkInLink();
      this.getNetworkInAddlink();
      if (this.graphRawData.links) {
        this.link_in_graph = [];
        this.check_switch = [];
        this.edges = [];
        this.graphEdge = [];
        this.graphNode = [];
        this.check = [];
        let nodes_ = {};
        let id = 1;
        // Max - Min in API
        this.graphRawData.links.forEach((link, i) => {
          // Calculate link usage
          const speed = this.calculate_usage_percent(
            Math.max(link.src_in_use, link.src_out_use),
            Math.max(link.dst_in_use, link.dst_out_use),
            link.link_min_speed
          );
          let color;
          if (speed < 50) {
            color = "rgb(144, 238, 144)";
          } else if (speed < 85) {
            color = "rgb(255, 165, 0)";
          } else {
            color = "rgb(255, 0, 0)";
          }
          const edgeId = `${link.src_if_ip}-${link.dst_if_ip}`;
          // Todo Fix highlight edges
          this.highlightNode.forEach(node => {
            if (
              node.indexOf(link.src_node_ip) > -1 ||
              node.indexOf(link.dst_node_ip) > -1
            ) {
              color = "rgb(0, 0, 153)";
            }
          });
          var ifaces = this.findInterfaces(link.src_node_id, link.dst_node_id, link.src_ip);
          const edge = {
            from: link.src_node_ip,
            to: link.dst_node_ip,
            width: link.link_min_speed / 400000,
            // value: link.src_in_use + link.dst_in_use,
            label: this.getNetworkFromIP(link.src_ip, ifaces.subnet)+"/"+ this.subnetToCidr(ifaces.subnet) +"("+ `${speed.toFixed(2)}%` + ")",
            id: edgeId,
            color: { color, highlight: color }
          };
          if (link.link_min_speed > 1544000) {
            edge.width = 1544000 /400000;
          }
          if(link.src_ip != link.dst_ip) {
            this.check.push(this.getNetworkFromIP(link.src_ip, ifaces.subnet));
            if (this.addlink.indexOf(link.src_ip) >= 0 && this.addlink.indexOf(link.dst_ip) >= 0 && this.count(this.network_in_link, this.getNetworkFromIP(link.src_ip, ifaces.subnet)) <= 1 && ifaces.admin_status == 1 && ifaces.operational_status == 1) {
              this.graphEdge.push(edge);
              this.graph.addEdge(link.src_node_ip, link.dst_node_ip);
              this.edges.push(link.src_node_ip, link.dst_node_ip);
              if (!this.router_in_graph.includes(link.src_node_ip)){
                this.router_in_graph.push(link.src_node_ip);
              }
              if (!this.router_in_graph.includes(link.dst_node_ip)){
                this.router_in_graph.push(link.dst_node_ip);
              }
            }
          }
          if (!nodes_[link.src_node_ip]) {
            let label;
            switch (this.node_label) {
              case "hostname":
                label = link.src_node_hostname;
                break;
            }
            nodes_[link.src_node_ip] = {
              id: link.src_node_ip,
              value: 1,
              label: label
            };
            id++;
          }
          if (!nodes_[link.dst_node_ip]) {
            let label;
            switch (this.node_label) {
              case "hostname":
                label = link.dst_node_hostname;
                break;
            }
            nodes_[link.dst_node_ip] = {
              id: link.dst_node_ip,
              value: 1,
              label: label
            };
            id++;
          }
        });
        // show switch
        for (var i=0; i < this.neighbor.length; i++){
          for (var j=0; j< this.neighbor[i].length; j++){
            if (this.check_switchs(this.neighbor[i][j].capabilities) && this.click == 1){
              let label = this.neighbor[i][j].name;
              nodes_[this.neighbor[i][j].name] = {
                id: this.neighbor[i][j].name,
                value: 1,
                label: label,
                color: "#FFFF80"
              }
            };
            id++;
            if (this.check_switchs(this.neighbor[i][j].capabilities) && this.click == 1){
              let color = "rgb(144, 238, 144)";
              
              for (var a=0; a<this.devices.length; a++){
                if (this.devices[a].device_ip == this.neighbor[i][j].device_ip){
                  var ifaces = this.devices[a].interfaces[this.neighbor[i][j].local_ifindex-1];
                  var net = this.getNetworkFromIP(ifaces.ipv4_address, ifaces.subnet);
                  const edge = {
                    from: this.neighbor[i][j].name,
                    to: this.neighbor[i][j].device_ip,
                    id: this.neighbor[i][j].name+this.neighbor[i][j].device_ip,
                    color: { color, highlight: color },
                    width: 1544000 / 400000
                  }
                  if (this.graphEdge.map(function(e) { return e.id; }).indexOf(edge.id) < 0) {
                    this.graphEdge.push(edge);
                    this.graph.addEdge(this.neighbor[i][j].name, this.neighbor[i][j].device_ip);
                    this.link_in_graph.push([this.neighbor[i][j].device_ip, this.neighbor[i][j].name, net]);
                    this.edges.push(this.neighbor[i][j].name, this.neighbor[i][j].device_ip);
                    this.check_switch.push(this.neighbor[i][j].name);
                  }
                }
              }
            }
          }
        }
        //show network
        for (var i=0; i < this.networks.length; i++){
          if (!nodes_[this.networks[i]] && (this.count(this.network_in_addlink, this.networks[i]) > 2 && this.count(this.network_in_link, this.networks[i]) >= 2) || (((this.source == this.networks[i] && this.count(this.network_in_link, this.source) >= 2) || (this.source == this.networks[i] && this.network_in_link.indexOf(this.networks[i]) < 0) || (this.destination == this.networks[i] && this.network_in_link.indexOf(this.networks[i]) < 0) || this.destination == this.networks[i] && this.count(this.network_in_link, this.destination) >= 2) && this.click == 1)) {
            let label = this.networks[i]+"/"+this.mask[i];
            nodes_[this.networks[i]] = {
              id: this.networks[i],
              value: 1,
              label: label,
              color: "#FFF"
            };
            id++;
            for (var a=0; a<this.link_in_graph.length; a++){
              if (this.link_in_graph[a][2] == this.networks[i] && !this.net_switch.includes(this.networks[i])){
                this.check_switch.push(this.link_in_graph[a][1]);
                let color = "rgb(144, 238, 144)";
                const edge = {
                  from: this.link_in_graph[a][1],
                  to: this.networks[i],
                  id: this.link_in_graph[a][0]+this.networks[i],
                  color: { color, highlight: color },
                  width: 1544000 / 400000
                }
                if (this.graphEdge.map(function(e) { return e.id; }).indexOf(edge.id) < 0) {
                  this.graphEdge.push(edge);
                  this.graph.addEdge(edge.from, this.networks[i]);
                  this.edges.push(edge.from, this.networks[i]);
                  this.net_switch.push(this.networks[i]);
                }
              }
            }
            for (var j=0; j < this.devices.length; j++) {
              for (var k=0; k < this.devices[j].interfaces.length; k++) {
                if (this.devices[j].interfaces[k].ipv4_address) {
                  if(this.getNetworkFromIP(this.devices[j].interfaces[k].ipv4_address, this.devices[j].interfaces[k].subnet) == this.networks[i] && !this.net_switch.includes(this.networks[i])) {
                    let color = "rgb(144, 238, 144)";
                    const edge = {
                      from: this.devices[j].interfaces[k].device_ip,
                      to: this.networks[i],
                      id: this.devices[j].interfaces[k].device_ip+this.networks[i],
                      color: { color, highlight: color },
                      width: 1544000 / 400000
                    }
                    
                    if (this.graphEdge.map(function(e) { return e.id; }).indexOf(edge.id) < 0) {
                      this.graphEdge.push(edge);
                      this.graph.addEdge(edge.from, this.networks[i]);
                      this.edges.push(edge.from, this.networks[i]);
                    }
                  }
                }
              }
            }
          };
        }
        if (this.click == 1){
          //alert(this.edges);
          for (var i=0; i<this.devices.length; i++){
            if (this.count(this.edges, this.devices[i].device_ip) < 2){
              delete nodes_[this.devices[i].device_ip];
            }
          }
          var check = [];
          //alert(this.check_switch);
          for (var i=0; i<this.check_switch.length;i++){
            if (this.count(this.check_switch, this.check_switch[i]) < 2){
              delete nodes_[this.check_switch[i]];
            }
            else if (!check.includes(this.check_switch[i])){
              check.push(this.check_switch[i]);
              for (j=0;j<this.edges.length;j=j+2){
                if (this.check_switch[i] == this.edges[j] && this.networks.includes(this.edges[j+1])){
                  check.push(this.check_switch[i]);
                }
              }
            }
          }
          for (var i=0; i<check.length;i++){
            if (this.count(check, check[i]) < 2){
              delete nodes_[check[i]];
            }
          }
        }
        this.nodes_ = nodes_;
        this.graphNode = Object.values(nodes_);
      }
    }
  },
  
  async mounted() {
    // console.log(jsnx)
    this.graph = new jsnx.Graph();
    this.interval = setInterval(() => this.fetchGraph(), 5000);
    try {
      let res = await this.$axios.$get("device");
      this.devices = res.devices;
      res = await this.$axios.$get("link");
      this.links = res.links;
      res = await this.$axios.$get(`flow/routing`);
      this.flow_routing = res.flows;
      let res2;
      let device;
      for (var i = 0; i < this.devices.length; i++) {
        device = this.devices[i];
        res2 = await this.$axios.$get(`routes/${device._id.$oid}`);
        if (res2) {
          this.routes.push(res2.routes);
        }
      }
      for (var i = 0; i < this.devices.length; i++) {
        device = this.devices[i];
        res2 = await this.$axios.$get(`device/${device._id.$oid}/neighbor`);
        if (res2) {
          this.neighbor.push(res2.neighbor);
        }
      }

      this.getNetwork();
    } catch (e) {}
    this.form = {
      ...this.propForm
    };
  },
  beforeDestroy() {
    clearInterval(this.interval);
  }
};
</script>

