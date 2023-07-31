#!/bin/sh

# Get last image id
last_image_id=$(cat image_id.txt)

# Remove last docker image if needed
if [ -z "$last_image_id" ]
then
      echo "Last image not found"
else
      docker image rm -f "$last_image_id"
      echo "Removed last image, id: '$last_image_id'"
fi

# Reset image_id.txt file
rm image_id.txt
touch image_id.txt

# Remove last build code directory
rm -rf server_api_build

# Create new build code directory
mkdir server_api_build

# Copy api files
cp -r ../server_api server_api_build
cp ../__init__.py server_api_build
cp ../app.py server_api_build

# Dockerfile
cp Dockerfile server_api_build

# Requirements
cp requirements.txt server_api_build

# Server utils
cp -r ../../server_utils server_api_build

# Get version as tag
version=$(cat ../../version.txt)

# Build docker
docker build -t server_api:"$version" server_api_build

# Getting the image id
image_id=$(docker images --format "{{.ID}}" --filter=reference=server_api:"$version" | head -n1)
echo "$image_id" > image_id.txt
echo "New image id: $image_id"

# Save image
# docker save server_api:"$version" -o ./server_api_"$version"_"$image_id".tar

# Getting IP Address
ip_address=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | awk '{print $1}' | sed -n 2p)
echo "IP address: '$ip_address'"

# Run docker
docker run --network="host" -e CONNECTION_STRING="mongodb://$ip_address:27017/" -p 5000:5000 "$image_id"

# Show current running images
docker ps