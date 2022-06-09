<template>
  <div>
    <b-container id="con">
      <b-row class="row">
        <b-col>
          <v-network-graph 
          v-model:selected-edges="selectedEdges"
          :nodes="nodes"
          :layouts="layouts"

          :edges="edges"
          :configs="configs"/>
        </b-col>
        <b-col>
          <b-tabs content-class="mt-3">
            <b-tab title="Flow Stats">
              <b-row id="filter_input">
                <b-col>
                  <label for="tags-port">Add Port Number Filters</label>
                  <b-form-tags tag-variant="primary" 
                  input-id="tags-port" 
                  placeholder="Enter new Port Number" 
                  size="sm"
                  v-model="filters.port_num"></b-form-tags>
                  <label for="tags-srcip">Add Source IP Number Filters</label>
                  <b-form-tags tag-variant="primary" 
                  input-id="tags-srcip" 
                  placeholder="Enter new Source IP" 
                  size="sm"
                  v-model="filters.src_ip"></b-form-tags>
                  <label for="tags-dstip">Add Destination IP Filters</label>
                  <b-form-tags tag-variant="primary" 
                  input-id="tags-dstip" 
                  placeholder="Enter new Destination IP" 
                  size="sm"
                  v-model="filters.dst_ip"></b-form-tags>
                  <b-button variant="outline-primary" size="sm" v-on:click="clearFilter">Clear Filter</b-button>
                </b-col>
                <b-col>
                  <div v-if="selectedEdges.length === 1">
                    <h6>Link Ultilization {{`${(getLinkUtilization(selectedEdge) * 100).toFixed(2)}%`}}</h6>
                    <b-progress max="1"  >
                      <b-progress-bar
                      :value="getLinkUtilization(selectedEdges[0])"
                      :variant="getProgressStyle(getLinkUtilization(selectedEdge))"
                      >
                      </b-progress-bar>
                    </b-progress>
                    <h6>Link Bandwidth: {{edges[selectedEdge].link_min_speed}} bps</h6>
                    <h6>Utilization Threshold</h6>
                    <b-form-input id="threshold" size="sm" v-model="threshold_input"></b-form-input>
                    <b-button size="sm" variant="info" v-on:click="setLinkThreshold">Set Threshold</b-button>
                  </div>
                  
                </b-col>
              </b-row>
              <b-row v-if="selectedEdges.length === 1" >
                <h4>
                  <b-badge size="sm" variant="warning">
                    {{getSourceFromEdgeName(selectedEdges[0]) + " - " + getDestinationFromEdgeName(selectedEdges[0])}}
                  </b-badge>
                </h4>
                <h6>Link's Flows Informations</h6>
                <div id="link_info">
                  <b-card size="sm" v-for="(flow, index) in selectedEdgeFlows" :key="index"
                  variant="info"
                  :header='"Source IP: "+ flow.src_ip + ", Destination IP: " + flow.dst_ip'
                  :sub-title='"Source Port: "+ flow.src_port + ", Destination Port: " + flow.dst_port'>
                  <b-card-text>
                    <p>Next Hop IP: <b-badge variant="primary">{{flow.next_hop_ip}}</b-badge></p>
                    <p v-if="flow.flow_rate !== ''">Flow Rate: <b-badge variant="info">{{flow.flow_rate}}</b-badge></p>
                  </b-card-text>
                  </b-card>
                </div>
              </b-row>
            </b-tab>
            <b-tab title="Policy Routing">
              <div id="policy_list">
                <b-card size="sm" v-for="(policy, index) in policy_list" :key="index"
                  variant="info"
                  >
                  <template #header>
                    <b-row>
                      <b-col cols="9"><h6>Policy Name: {{policy?.name}}</h6></b-col>
                      <b-col cols="3"><b-button size="sm" variant="danger"
                      v-on:click="removePolicy(policy?.flow_id.toString())"
                      >Remove Policy</b-button></b-col>
                    </b-row>
                    
                  </template>
                  <b-row>
                    <b-col cols="10">
                      <!-- :sub-title='"Status: " + (policy.info.status === 3?"Active":"Not Active")' -->
                      <b-card-text>
                        <p>Source IP: <b-badge variant="primary">{{policy?.src_ip}}</b-badge>
                        Wildcard: <b-badge variant="primary">{{policy?.src_wildcard}}</b-badge>
                        Port: <b-badge variant="primary">{{policy?.src_port}}</b-badge>
                        </p>
                      </b-card-text>
                    </b-col>
                  </b-row>
                  <b-row>
                    <b-col cols="10">
                      <!-- :sub-title='"Status: " + (policy.info.status === 3?"Active":"Not Active")' -->
                      <b-card-text>
                        <p>Destination IP: <b-badge variant="primary">{{policy?.dst_ip}}</b-badge>
                        Wildcard: <b-badge variant="primary">{{policy?.dst_wildcard}}</b-badge>
                        Port: <b-badge variant="primary">{{policy?.dst_port}}</b-badge>
                        </p>
                      </b-card-text>
                    </b-col >
                  </b-row>
                  <b-row>
                    <table>
                      <thead>
                        <tr>
                          <th v-for="(h, i) in ['Device', 'Action', 'Target']" :key="i">{{h}}</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(d, i) in policy?.actions.map(
                          d => ({
                              'Device': getDeviceNamebyID(d.device_id.$oid),
                              'Action': ['Drop', 'Next-Hop-IP', 'Next-Hop-Interface'][d.action - 1],
                              'Target': d.data
                                })
                        )" :key="i"
                        >
                        <td>{{d.Device}}</td>
                        <td>{{d.Action}}</td>
                        <td>{{d.Target}}</td>
                        </tr>
                      </tbody>
                    </table>
                  </b-row>
                  
                  <!-- <b-col cols="2">
                    
                  </b-col> -->
                  
                </b-card>
              </div>
            </b-tab>
            <b-tab title="Add Policy Routing">
              <b-form-row>
                <b-col cols="5">
                  <label for="policy-name">Policy Name</label>
                  <b-form-input v-model="policy.name" size="sm" id="policy-name"></b-form-input>
                </b-col>
              </b-form-row>
              <b-form-row id="policy_input">
                <b-col cols="3">
                  <label for="src-ip">Source IP</label>
                  <b-form-input v-model="policy.src_ip" size="sm" id="src-ip"></b-form-input>
                  <label for="dst-ip">Destination IP</label>
                  <b-form-input v-model="policy.dst_ip" size="sm" id="dst-ip"></b-form-input>
                </b-col>
                <b-col>
                  <label for="src-netmask">Source Wildcard</label>
                  <b-form-input v-model="policy.src_netmask" size="sm" id="src-netmask"></b-form-input>
                  <label for="dst-netmask">Destination Wildcard</label>
                  <b-form-input v-model="policy.dst_netmask" size="sm" id="dst-netmask"></b-form-input>
                </b-col>
                <b-col>
                  <label for="src-netmask">Source Port(num or any)</label>
                  <b-form-input v-model="policy.src_port" size="sm" id="src-port"></b-form-input>
                  <label for="dst-netmask">Destination Port(num or any)</label>
                  <b-form-input v-model="policy.dst_port" size="sm" id="dst-port"></b-form-input>
                </b-col>
              </b-form-row>
              <b-row>
                <b-col cols="4"><label for="policy_device">Device</label></b-col>
                <b-col cols="3"><label for="policy_action">Action</label></b-col>
                <b-col cols="4"><label v-if="action_devices[0].action !== '1' && action_devices[0].action !== ''" 
                  for="policy_data">Action Target</label></b-col>
              </b-row>
              <b-form-row v-for="(_, index) in action_devices" :key="index">
                <b-col cols="4">
                  
                  <b-form-select id="policy_device" v-model="action_devices[index].device" size="sm" class="mt-3">
                    <b-form-select-option v-for="(node, index) in getDevicesArray()" :key="index"
                    :value="node.name">{{node.name + '(' + node.management_ip + ')'}}</b-form-select-option>
                  </b-form-select>
                </b-col>
                <b-col cols="3">
                  
                  <b-form-select id="policy_action" v-model="action_devices[index].action" size="sm" class="mt-3">
                    <b-form-select-option value=1>Drop</b-form-select-option>
                    <b-form-select-option value=2>Next-Hop IP</b-form-select-option>
                    <b-form-select-option value=3>Interface</b-form-select-option>
                  </b-form-select>
                </b-col>
                <b-col cols="3">
                  
                  <b-form-select id="policy_data" v-if="action_devices[index].action !== '1' && action_devices[index].action !== ''" 
                  :options="action_devices[index].action === '2'?nodes[action_devices[index].device].next_hop_ip:nodes[action_devices[index].device].interfaces"
                  v-model="action_devices[index].data"
                  size="sm" class="mt-3">
                  </b-form-select>
                </b-col>
                <b-col cols="2">
                  <b-button pill variant="outline-danger" size="sm" v-on:click="action_devices.splice(index, 1)">Remove</b-button>
                </b-col>
              </b-form-row>
              <b-button size="sm" v-on:click="action_devices.push({'device':'', 'action':'', 'data':''})">Add more device</b-button>
              <b-button size="sm" v-on:click="addPolicy" variant="success">Add Policy</b-button>
            </b-tab>
            
          </b-tabs>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, reactive, watchEffect, ref, watch } from "vue";
import { Nodes, Edges, getFullConfigs, EventHandlers } from "v-network-graph";
// import * as vNG from "v-network-graph"
// import {ForceLayout} from "@/node_modules/v-network-graph/lib/layouts/force-layout"
import client from "@/apiclient";
import "/node_modules/vue-scrolling-table/dist/style.css"
import Swal from 'sweetalert2'

export default defineComponent({
  name: "Home",
  setup() {
    const portnum = ref<string>("");
    const filters = reactive({
      port_num: ref<number[]>([]),
      src_ip: ref<string[]>([]),
      dst_ip: ref<string[]>([])
    });
    const nodes = reactive({});
    const edges = reactive({});
    const layouts = reactive({});
    const flows = reactive({});
    const selectedEdges = ref<string[]>([]);
    const selectedEdge = ref<string>("");
    const selectedEdgeFlows = ref<any[]>([]);
    const selectedNodes = ref<string[]>([]);
    const selectedNode = ref<string>("");
    const policy_list = reactive({});

    const tooltip = ref<HTMLDivElement>()
    const tooltipOpacity = ref(0)
    const targetNodeId = ref("")
    
    const configs = reactive(getFullConfigs())
    configs.node.selectable = true;
    configs.edge.selectable = edge => edge.selectable;
    configs.edge.normal.width = edge => edge.animate ? 3 : 2;
    configs.edge.normal.dasharray = edge => edge.animate ? "5" : "0"
    configs.edge.normal.animate = edge => !!edge.animate
    // configs.edge.marker.source.type = 'arrow'
    configs.node.draggable = true;
    configs.node.normal.color = node => node.color
    const src_ip = ref<string>("");
    const dst_ip = ref<string>("");
    const threshold_input = ref<string>("1");
    const action_devices = ref<any[]>([{'device':"", "action":"", "data":""}]);
    const device_choices = reactive({});

    const policy = reactive({
      name:'',
      device_management_ip:'',
      src_ip:'',
      src_netmask:'',
      src_port:'',
      dst_ip:'',
      dst_netmask:'',
      dst_port:'',
      action:'',
      outgoing:'',
    });

    async function fetchNetwork(nodes: Nodes, edges: Edges, layouts: any): Promise<void> {
      const {
        data: { graph, status },
      } = await client.getAll();
      const newNodes = graph.nodes;
      const newEdges = graph.edges;
      const newLayouts = graph.layout;
      // const newChoices = 
      Object.assign(nodes, newNodes);
      Object.assign(layouts, newLayouts);
      Object.assign(edges, newEdges);
      
      if(status === "ok")
        Swal.fire({title: "Topology Loaded", icon:"success", timer:2000})
      // console.log('done')
    }

    async function fetchNetworkFlow(nodes: Nodes, edges: Edges, filters:any, layouts: any): Promise<void> {
      const {
        data: { graph, flows_data },
      } = await client.postFilters(filters);
      const newNodes = graph.nodes;
      const newEdges = graph.edges;
      // const newLayouts = graph.layout;

      Object.assign(flows, flows_data)
      Object.assign(nodes, newNodes);
      Object.assign(edges, newEdges);
      // Object.assign(layouts, newLayouts);

      // console.log(nodes)
      // console.log(edges)
      // console.log(layouts)
      // console.log('update flow done')
    }

    async function fetchPolicy(): Promise<void> {
      const { data } = await client.getPolicyRouting();
      Object.assign(policy_list, data.flows)
    }

    const eventHandlers: EventHandlers = {
      "node:pointerover": ({ node }) => {
        targetNodeId.value = node
        tooltipOpacity.value = 1 // show
      },
      "node:pointerout": _ => {
        tooltipOpacity.value = 0 // hide
      },
    }

    function getDevicesArray(): unknown[]{
      const devices: unknown[] = [];
      for (const node in nodes){
        if(!nodes[node].name.includes("/"))
          devices.push(nodes[node])
      }
      // console.log(devices)
      return devices;
    }

    function addPortFilter(): void {
      if (portnum.value === ""){
        return ;
      }
      const port = parseInt(portnum.value);
      if (!filters.port_num.includes(port)) {
        filters.port_num.push(port);
      }
      portnum.value = "";
      fetchNetworkFlow(nodes, edges, {"filters":filters}, layouts)
    }

    function addSourceFilter(): void {
      if (src_ip.value === ""){
        return ;
      }
      const src = src_ip.value;
      if (!filters.src_ip.includes(src)) {
        filters.src_ip.push(src);
      }
      src_ip.value = "";
      fetchNetworkFlow(nodes, edges, {"filters":filters}, layouts)
    }

    function addDestFilter(): void {
      if (dst_ip.value === ""){
        return ;
      }
      const dst = dst_ip.value;
      if (!filters.dst_ip.includes(dst)) {
        filters.dst_ip.push(dst);
      }
      dst_ip.value = "";
      fetchNetworkFlow(nodes, edges, {"filters":filters}, layouts)
    }

    function getDeviceNamebyID(id: string): string{
      for(const node in nodes){
        if(nodes[node].device_id === id)
          return nodes[node].name
      }
      return "removed device"
    }

    async function removePolicy(flow_id: string): Promise<void>{
      const  data  = await client.deletePolicyRouting(flow_id)
      console.log(data)
      if(data){
        Swal.fire({title:"Remove Policy Successful", icon:"success", confirmButtonText:"Okay"})
      }
      else{
        Swal.fire({title:"Error during the process", icon:"error", confirmButtonText:"Okay"})
      }
    }

    async function addPolicy(): Promise<void>{

      const actions: unknown[] = [];
      // console.log(action_devices)
      for(const action in action_devices.value){
        actions.push({
          'device_id': nodes[action_devices.value[action].device].device_id,
          'action': parseInt(action_devices.value[action].action),
          'data': action_devices.value[action].data
        })
      }
      console.log(actions)

      const {
        data: {success}
      } = await client.addPolicyRouting(
        {
          'name': policy.name,
          'src_ip': policy.src_ip,
          'src_port': policy.src_port,
          'src_subnet': policy.src_netmask,
          'dst_ip': policy.dst_ip,
          'dst_port': policy.dst_port,
          'dst_subnet': policy.dst_netmask,
          'actions': actions
        })
      if(success){
        Swal.fire({title:"Add Policy Successful", icon:"success", confirmButtonText:"Okay"})
      }
      else{
        Swal.fire({title:"Error during the process", icon:"error", confirmButtonText:"Okay"})
      }
    }

    async function setLinkThreshold(){
      const {
        data: { success }
      } = await client.setLinkUtilization({
        'link_id':edges[selectedEdge.value]['link_id'],
        'utilization_threshold': parseFloat(threshold_input.value)
      });
      if(success){
        Swal.fire({title:"Set Link Utilization Successful", icon:"success", confirmButtonText:"Okay"})
      }
      else{
        Swal.fire({title:"Error during the process", icon:"error", confirmButtonText:"Okay"})
      }
    } 


    watch(
      ()=>selectedEdges.value[0],
      ()=>{
        selectedEdge.value = selectedEdges?.value[0]
        // fetchNetworkFlow(nodes, edges, {"filters":filters}, layouts)
        selectedEdgeFlows.value = flows[selectedEdge.value]
        threshold_input.value = edges[selectedEdge.value]?.utilization_threshold
        
        
        // Object.assign(selectedEdgeFlows, flows[selectedEdge.value])
        // edges[selectedEdge].animate = true
        // console.log(selectedEdge)
      }
    )

    function getLinkUtilization(edgeName){
      const edge = edges[edgeName]
      const utilzation = edge.utilization
      // console.log(utilzation)
      return utilzation
    }

    function getProgressStyle(utilization){
      const util = utilization
      return  util<0.5?'success':util<0.75?'warning':'danger'
    }

    function getSourceFromEdgeName(edgeName): string{
      const edge = edges[edgeName]
      const src = nodes[edge.source].name
      return src
    }

    function getDestinationFromEdgeName(edgeName): string{
      const edge = edges[edgeName]
      const dst = nodes[edge.target].name
      return dst
    }

    // function get

    function clearFilter(): void{
      filters.src_ip.splice(0, filters.src_ip.length)
      filters.dst_ip.splice(0, filters.dst_ip.length)
      filters.port_num.splice(0, filters.port_num.length)
      fetchNetworkFlow(nodes, edges, {"filters":filters}, layouts)
    }

    onMounted(() => {
      fetchNetwork(nodes, edges, layouts);
      fetchPolicy();
      setInterval(()=>fetchNetworkFlow(nodes, edges, {"filters":filters}, layouts), 1000);
      setInterval(()=>fetchPolicy(), 1000);

    });
    watchEffect(() => {
      
      // fetchNetwork(nodes, edges);
    });
    return { 
      nodes, edges, layouts, 
      configs, portnum, filters, 
      policy, selectedEdges, selectedEdge, policy_list,
      selectedEdgeFlows, src_ip, dst_ip, threshold_input, device_choices, action_devices, 
      addPortFilter, clearFilter, fetchNetwork, getSourceFromEdgeName, getDestinationFromEdgeName, fetchNetworkFlow,
      addSourceFilter, addDestFilter, getLinkUtilization, getProgressStyle, setLinkThreshold, getDevicesArray, addPolicy,
      getDeviceNamebyID, removePolicy
      };
  },
});
</script>
<style scoped>
#con {
  border: 1px solid rgb(109, 170, 255);
  height: 80vh;
  overflow: hidden;
}
.v-network-graph {
  position:relative;
  top: 10px;
  border: 1px solid rgb(109, 170, 255);
  height: inherit;
}

#table_parent {
  left: 10vw;
  top: 15vh;
  height: 75vh;
  width:100%;
  overflow: hidden;
}

#policy_list {
  overflow: scroll;
  height: 75vh;
}



#filter_input, #Filters {
  display:flexbox;
  padding: 10px;
}

input {
  margin: 5px;
}

button {
  margin: 5px;
}


#link_info {
  height: 40vh;
  overflow: scroll;
}

</style>
