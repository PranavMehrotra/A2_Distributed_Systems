# Import necessary modules
from aiohttp import web
from manager import Manager

mgr = Manager()  ### Add user and password here of SQL server
server_id = ""

# Config endpoint to initialize the database
async def config(request):
    try:
        print("Config endpoint called")

        # Get the JSON data from the request
        request_json = await request.json() 
        # Call the Config_database method of the Manager class 
        message, status = mgr.Config_database(request_json)

        # Create a response JSON
        if status == 200:
            shards = request_json.get('shards', [])
            message = ", ".join([f"{server_id}:{shard}" for shard in shards]) + " configured"
            
            response_json = {
                "message": message,
                "status": "success"
            }
            
        else:
           # fail json message
            response_json = {
                "error": str(message),
                "status": "failure"
            }
        
        return web.json_response(response_json, status=status)

    except Exception as e:
        print(f"Server: Error in Config endpoint: {str(e)}")
        return web.json_response({"error": "Internal Server Error"}, status=500)

# Heartbeat endpoint to check if the server is running    
async def heartbeat(request):
    try:
        return web.Response(status=200)
    
    except Exception as e:
        print(f"Server: Error in heartbeat endpoint: {str(e)}")
        return web.json_response({"error": "Internal Server Error"}, status=500)

# Copy endpoint to return database entries
async def copy_database(request):
    try:
        print("Copy endpoint called")
        # Get the JSON data from the request
        request_json = await request.json()         
        database_copy, status = mgr.Copy_database(request_json)
        
        # Create a response JSON
        if status == 200:
            response_json = {}
            
            # Remove the first column (auto increment ID column) from each row
            for shard_name, shard_data in database_copy.items():
                updated_shard_data = [[row[1:], ] for row in shard_data]
                response_json[shard_name] = updated_shard_data
            
            response_json["status"] = "success"
            
        else:
            message = database_copy
            response_json = {
                "error": message,
                "status": "failure"
            }
        return web.json_response(response_json, status=status)
    
    except Exception as e:
        
        print(f"Server: Error in copy endpoint: {str(e)}")
        return web.json_response({"error": "Internal Server Error"}, status=500)

# Read endpoint to return database entries where Stud_id>= low and Stud_id < high
async def read_database(request):
    try:
        print("Read endpoint called")
        # Get the JSON data from the request
        request_json = await request.json()  
        database_entry, status = mgr.Read_database(request_json)
        
        # Create a response JSON
        if status==200:
            umodified_list = [(item[1], item[2], item[3]) for item in database_entry]
            response_data = {
                    "data": umodified_list,
                    "status": "success"
                }
        else:
            message = database_entry
            response_data = {
                    "error": message,
                    "status": "failure"
                }
    
        return web.json_response(response_data, status=status)
   
    except Exception as e:
    
        print(f"Server: Error in read endpoint: {str(e)}")
        return web.json_response({"error": "Internal Server Error"}, status=500)

# Write endpoint to add a new entry to the database
async def write_database(request):
    
    try:
        print("Write endpoint called")
        # Get the JSON data from the request
        request_json = await request.json()  
        message, status,id = mgr.Write_database(request_json)
        
        if status == 200:
            response_data = {
                    "message": message,
                    "current_idx":id,
                    "status": "success"
                }
            
        else:
            response_data = {
                    "error": message,
                    "current_idx":id,
                    "status": "failure"
                }
            
        return web.json_response(response_data, status=status)  
    
    except Exception as e:
        
        print(f"Server: Error in write endpoint: {str(e)}")
        return web.json_response({"error": "Internal Server Error"}, status=500)  

# Update endpoint to update an existing entry in the database
async def update(request):
    
    try:
        print("Update endpoint called")
        # Get the JSON data from the request
        request_json = await request.json()  
        stud_id = request_json.get("Stud_id",[])
        message, status = mgr.Update_database(request_json)
    
        # Create a response JSON
        if status == 200:
            response_data = {
                "message": f"Data entry for Stud_id:{stud_id} updated",
                "status": "success"
            }
            return web.json_response(response_data, status=status)
        
        else:
            response_data = {
                "message": f"{str(message)}",
                "status": "failure"
            }
            return web.json_response(response_data, status=status)        
        
    except Exception as e:
        
        print(f"Server: Error in update endpoint: {str(e)}")
        return web.json_response({"error": "Internal Server Error"}, status=500)

# Delete endpoint to remove an entry from the database
async def del_database(request):
    
    try:
        print("Delete endpoint called")
        # Get the JSON data from the request
        request_json = await request.json()  
        stud_id = request_json.get("Stud_id")
        message, status = mgr.Delete_database(request_json)

        if status==200:
            response_data = {
                "message": f"Data entry with Stud_id:{stud_id} removed",
                "status": "success"
            }
        
        else:
            response_data = {
                "error": f'{str(message)}',
                "status": "failure"
            }    
        
        return web.json_response(response_data, status=status)
   
    except Exception as e:
        
        print(f"Server: Error in delete endpoint: {str(e)}")
        return web.json_response({"error": "Internal Server Error"}, status=500)

# Catch-all endpoint for any other request
async def not_found(request):
    return web.Response(text="Not Found", status=400)


# Define the main function to run the web server
def run_server():
    # Create an instance of the web Application
    app = web.Application()

    # Add routes for the home and heartbeat endpoints
    app.router.add_post('/config', config)
    app.router.add_get('/heartbeat', heartbeat)
    app.router.add_get('/copy', copy_database)
    app.router.add_post('/read', read_database)
    app.router.add_post('/write', write_database)
    app.router.add_put('/update', update)
    app.router.add_delete('/del', del_database)


    # Add a catch-all route for any other endpoint, which returns a 400 Bad Request
    app.router.add_route('*', '/{tail:.*}', not_found)

    # Run the web application on port 5000
    web.run_app(app, port=5000)

# Entry point of the script
if __name__ == '__main__':
    print("Starting server...")

    # Get the server_id from the environment variable
    server_id = 'Server0' #os.environ.get("SERVER_ID"
    # # Run the web server
    print("\nHi.", flush=True)
    run_server()

