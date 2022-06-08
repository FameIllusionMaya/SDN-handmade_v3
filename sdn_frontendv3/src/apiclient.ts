import http from "@/httpclient";

class Client{
    getAll(): Promise<any> {
        return http.get("/graph");
      }
    postFilters(filters: any){
        return http.post("/graph", filters);
     }
    postDevice(device_info: any){
      return http.post("/device", device_info)
    }
    patchDevice(device_info: any, device_id: string){
      return http.patch("/device/" + device_id, device_info)
    }
    deleteDevice(device_id_str: any){
      return http.delete("/device", {params:{device_id:device_id_str}})
    }
    getAllDevices(): Promise<any> {
      return http.get("/device");
    }
    initNetflow(payload: any){
      return http.post("/initialization", payload);
    }
    initSNMP(payload: any){
      return http.post("/initialization", payload);
    }
    setLinkUtilization(payload: any){
      return http.patch('/link', payload)
    }
    addPolicyRouting(payload: any){
      return http.post('/flow/routing', payload)
    }
    getPolicyRouting(){
      return http.get('/flow/routing')
    }
    deletePolicyRouting(flow_id_str: any){
      return http.delete('/flow/routing', {params:{flow_id:flow_id_str}})
    }
}

export default new Client();
