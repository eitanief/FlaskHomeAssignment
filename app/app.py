from flask import Flask, request, jsonify, Response
import threading, json

app = Flask(__name__)

# Fetch resources list from json file
with open('app/resources.json') as json_file:
    data = json.load(json_file).get("data")
resources = []

# wrap resources with availability property and a lock
for user in data:
    lock = threading.Lock()
    resources.append({"available": "true", "data": user, "lock": lock})


def handle_get():
    """
    Goes through the resources pool, fetches an available resource if there is one
    :return: json representation of an available resource. if no such resource, returns error response
    """
    for resource in resources:

        # acquire lock
        res_lock = resource.get("lock")
        res_lock.acquire()

        # Get if available
        if resource.get("available") == "true":
            # Available - acquire resource and return
            resource.update({"available": "false"})
            res_lock.release()
            return jsonify(resource.get("data"))

        # Not available, release and continue
        res_lock.release()

    # All resources are taken
    return app.make_response(('No available resource', 500))


def handle_post():
    """
    Receives a json object from the body as an argument.
    Goes through the resources pool, finds the resource matching the argument and releases it
    :return: success or failure response
    """
    for resource in resources:

        if resource.get("data").get("ip") == request.get_json().get("ip"):
            # acquire lock
            res_lock = resource.get("lock")
            res_lock.acquire()

            # POST if not available
            if resource.get("available") == "false":
                # Not available - release resource and return
                resource.update({"available": "true"})
                res_lock.release()
                return app.make_response(('Resource was successfully released', 200))

            else:
                # Resource is already available
                res_lock.release()
                return app.make_response(('Resource was already available', 200))

    # Could not find resource
    return app.make_response(('Resource not found', 500))


@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'GET':
        return handle_get()
    if request.method == 'POST':
        return handle_post()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7080)


