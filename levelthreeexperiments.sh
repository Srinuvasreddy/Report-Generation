aws servicecatalog provision-product --product-id prod-uugdzjvcqdv6k --provisioning-artifact-id pa-xjmf6ofgysu2o --provisioned-product-name AWS_FIS_L2_apigateway_abcde --path-id lpv3-6bqioqcfwlelm --provisioning-parameters Key=blockCode,Value=ITSSREBTSP Key=AppName,Value=shop --region us-east-1

#!/bin/bash
#Read input data
APP_NAME=$(grep APP_NAME ./params/${ENV}/${APP_NAME}/${BLOCK_CODE}/l3experiment.txt | cut -f2 -d"=")
REGION=$(grep REGION ./params/${ENV}/${APP_NAME}/${BLOCK_CODE}/l3experiment.txt | cut -f2 -d"=")
ENV=$(grep ENV ./params/${ENV}/${APP_NAME}/${BLOCK_CODE}/l3experiment.txt | cut -f2 -d"=")
ACCOUNT_ID=$(grep ACCOUNT_ID ./params/${ENV}/${APP_NAME}/${BLOCK_CODE}/l3experiment.txt | cut -f2 -d"=")
tag_name=$(grep chaos_experiment_name ./params/${ENV}/${APP_NAME}/${BLOCK_CODE}/l3experiment.txt | cut -f2 -d"=")

TargetSubnetOne=$(grep TargetSubnetOne ./params/${ENV}/${APP_NAME}/${BLOCK_CODE}/l3experiment.txt | cut -f2 -d"=")
TargetSubnetTwo=$(grep TargetSubnetTwo ./params/${ENV}/${APP_NAME}/${BLOCK_CODE}/l3experiment.txt | cut -f2 -d"=")
TargetSubnetThree=$(grep TargetSubnetThree ./params/${ENV}/${APP_NAME}/${BLOCK_CODE}/l3experiment.txt | cut -f2 -d"=")
block_code=$(grep block_code ./params/${ENV}/${APP_NAME}/${BLOCK_CODE}/l3experiment.txt | cut -f2 -d"=")

AWS_RESOURCE=$(grep AWS_RESOURCE ./params/${ENV}/${APP_NAME}/${BLOCK_CODE}/l3experiment.txt | cut -f2 -d"=")

#Launch Service Catalog Related Input data.
SERVICE_CATALOG_PRODUCT_ID_EAST=prod-c6tvmqeoa5eui
SERVICE_CATALOG_PRODUCT_ID_WEST=prod-qub464mg56tkw
ARTIFACTID_EAST=pa-55qhe7a3lpgby
ARTIFACTID_WEST=pa-2ieooq472akos
PATHID_EAST=lpv3-6bqioqcfwlelm
PATHID_WEST=lpv3-isb5c3mtkfiya
ROLE_NAME=SpokeArtifactDeployer
VAR_FILE_NAME=apigateway.json


# List experiment templates and save to a JSON file
templates_file="list-templates.json"
# Fetch experiment templates and save to a file
#aws fis list-experiment-templates --no-paginate > ${templates_file}
# Initial command to list experiment templates
aws fis list-experiment-templates > list-templates.json

echo "App Name is : ${APP_NAME}"
echo "Block Code is : ${block_code}"
echo "Account ID is : ${ACCOUNT_ID}"
echo "Chaos Experiment name is : ${tag_name}"
echo "Region is : ${REGION}"
echo "Env name is : ${ENV}"
echo "Subnet1 is : ${TargetSubnetOne}"
echo "Subnet2 is : ${TargetSubnetTwo}"
echo "Subnet3 is : ${TargetSubnetThree}"

# Initial command to list experiment templates
awsv2 fis list-experiment-templates --region ${REGION} > list-templates.json
# Extract nextToken without using jq
next_token=$(grep -o '"nextToken": *"[^"]*"' list-templates.json | awk -F: '{gsub(/[ ",]/, "", $2); print $2}')
if [[ "$next_token" != "" ]]; then
   echo "found token"
   # If nextToken exists, continue fetching the rest of the templates
   awsv2 fis list-experiment-templates --max-results 100 --next-token "$next_token" >> list-templates.json
else
   # Alternative command to get the template ID if no nextToken
   echo "No token"
fi

# Extract the template block
templates_file="list-templates.json"
template_block=$(awk '/"experimentTemplates": \[/{flag=1; next} /\]/{flag=0} flag {print}' ${templates_file})
# Extract the template ID based on the tag name
# Check if the templates file was created successfully
if [ ! -f "${templates_file}" ]; then
 echo "Failed to create templates file."
 exit 1
fi

TmplId=$(echo "$template_block" | awk -v RS='}' -v tag="$tag_name" '
/"tags": {[^}]*"Name": "'$tag_name'"/ {
match($0, /"id": "[^"]+"/);
if (RSTART) {
print substr($0, RSTART + 6, RLENGTH - 7);
exit;
}
}')

expTmplId=${TmplId:1}
echo "FIS Experiment Template ID - ${expTmplId}"

# Check if experiment template ID was found
if [ -z "$expTmplId" ]; then
        echo "*** AWS FIS Experiment Template ID NOT found, Service Catalog is launching now *** "
        # Default word length
        WORD_LENGTH=5
        # Check if a custom word length was provided as an argument
        if [ ! -z "$1" ]; then
          WORD_LENGTH=$1
        fi
          # Generate the random word
          UNIQUENO=$(cat /dev/urandom | tr -dc 'a-zA-Z' | fold -w $WORD_LENGTH | head -n 1)
          # Output the random word
          echo $UNIQUENO

   # Check if REGION contains 'east' or 'west'
        if [[ $REGION == "us-east-1" ]]; then
            SERVICE_CATALOG_PRODUCT_ID=$SERVICE_CATALOG_PRODUCT_ID_EAST
            ARTIFACTID=$ARTIFACTID_EAST
            PATHID=$PATHID_EAST
        elif [[ $REGION == "us-west-2" ]]; then
            SERVICE_CATALOG_PRODUCT_ID=$SERVICE_CATALOG_PRODUCT_ID_WEST
            ARTIFACTID=$ARTIFACTID_WEST
            PATHID=$PATHID_WEST
        else
            echo "Error: REGION must contain 'us-east-1' or 'us-west-2'."
            exit 1
        fi

        ASSUMED_ROLE_ACCOUNT=$(awsv2 sts get-caller-identity --output text --query Account)
        echo "Launching product in $REGION"
        echo "Switched to account: $ASSUMED_ROLE_ACCOUNT"
        awsv2 servicecatalog provision-product --product-id $SERVICE_CATALOG_PRODUCT_ID \
        --provisioning-artifact-id ${ARTIFACTID} \
        --provisioned-product-name AWS_FIS_L3_${AWS_RESOURCE}_${UNIQUENO} \
        --path-id ${PATHID} \
        --provisioning-parameters Key=blockCode,Value=${block_code} \
        --region ${REGION}

fi


# Create JSON input file for updating experiment template
jsonFile="./fis-${ACCOUNT_ID}-${REGION}.json"
echo "Created JSON File is ${jsonFile}"
sleep 60

if [ "$tag_name" == "Region_Failure" ]; then
   # 1 Modify the JSON structure differently for Region_Failure Experiment
   cat > $jsonFile <<EOF

{
        "id": "${expTmplId}",
        "roleArn": "arn:aws:iam::${ACCOUNT_ID}:role/Delta-FIS-Execution-Role",
        "targets": {
                        "Subnets-Target": {
                                "resourceType": "aws:ec2:subnet",
                                "resourceArns": [
                                        "arn:aws:ec2:${REGION}:${ACCOUNT_ID}:subnet/${TargetSubnetOne}",
                                        "arn:aws:ec2:${REGION}:${ACCOUNT_ID}:subnet/${TargetSubnetTwo}",
                                        "arn:aws:ec2:${REGION}:${ACCOUNT_ID}:subnet/${TargetSubnetThree}"
                                ],
                                "selectionMode": "ALL"
                        }
                },
        "actions": {
                "AZ_failure": {
                                "actionId": "aws:network:disrupt-connectivity",
                                "parameters": {
                                        "duration": "PT15M",
                                        "scope": "all"
                                },
                                "targets": {
                                        "Subnets": "Subnets-Target",

                                }
                        }
                }
}
EOF
elif [ "$tag_name" == "Multi_AZ_Failure" ]; then
   # 2 Modify the JSON structure differently for Multi_AZ_Failure Experiment
   cat > $jsonFile <<EOF
{
        "id": "${expTmplId}",
        "roleArn": "arn:aws:iam::${ACCOUNT_ID}:role/Delta-FIS-Execution-Role",
        "targets": {
                        "Subnets-Target": {
                                "resourceType": "aws:ec2:subnet",
                                "resourceArns": [
                                        "arn:aws:ec2:${REGION}:${ACCOUNT_ID}:subnet/${TargetSubnetOne}",
                                        "arn:aws:ec2:${REGION}:${ACCOUNT_ID}:subnet/${TargetSubnetTwo}"
                                ],
                                "selectionMode": "ALL"
                        }
                },
        "actions": {
                "AZ_failure": {
                                "actionId": "aws:network:disrupt-connectivity",
                                "parameters": {
                                        "duration": "PT15M",
                                        "scope": "all"
                                },
                                "targets": {
                                        "Subnets": "Subnets-Target"
                                }
                        }
                },
        "roleArn": "arn:aws:iam::${ACCOUNT_ID}:role/Delta-FIS-Execution-Role"
}
EOF
elif [ "$tag_name" == "Single_AZ_Failure" ]; then
   # 2 Modify the JSON structure differently for Single_AZ_Failure Experiment
   cat > $jsonFile <<EOF
{
      "id": "${expTmplId}",
      "roleArn": "arn:aws:iam::${ACCOUNT_ID}:role/Delta-FIS-Execution-Role",
      "targets": {
                "Subnets-Target": {
                        "resourceType": "aws:ec2:subnet",
                        "resourceArns": [
                                "arn:aws:ec2:${REGION}:${ACCOUNT_ID}:subnet/${TargetSubnetOne}",
                        ],
                        "selectionMode": "ALL"
                }
        },
        "actions": {
                        "Single_AZ_Failure": {
                                "actionId": "aws:network:disrupt-connectivity",
                                "parameters": {
                                        "duration": "PT15M",
                                        "scope": "all"
                                },
                                "targets": {
                                        "Subnets": "Subnets-Target"
                                }
                        }
                },
        "roleArn": "arn:aws:iam::${ACCOUNT_ID}:role/Delta-FIS-Execution-Role"
}
EOF
else
   echo "********* ERROR ---- Unknown Experiment Name Specified. Please verify and pass the Proper chaos_experiment_name as like Single_AZ_Failure or Multi_AZ_Failure or Region_Failure ***********"
   exit 1
fi

# Update experiment template
echo "FIS Experiment updating"
awsv2 fis update-experiment-template --region "${REGION}" --cli-input-json file://$jsonFile
sleep 60
# Start the experiment and get the experiment execution ID using grep and awk
expExecId=$(awsv2 fis start-experiment --region "${REGION}" --experiment-template-id ${expTmplId} --tags Name="${tag_name}" | grep -oP '"id": *"\K[^"]+(?=")')
echo ""
echo "FIS Experiment Execution ID - ${expExecId}"

statusIs=$(awsv2 fis get-experiment --region "${REGION}" --id "${expExecId}" --query 'experiment.state.status' --output text)
echo "Experiment status is ${statusIs}"
while [[ "$statusIs" == "running" || "$statusIs" == "initiating" ]]; do
    echo "Status: $statusIs"
    statusIs=$(awsv2 fis get-experiment --region "${REGION}" --id "${expExecId}" --query 'experiment.state.status' --output text)
    sleep 55
done
echo "Final Status: $statusIs"

if [ "$statusIs" == "failed" ]; then
        echo " Experiment is failed "
        exit 1  # Exit with a non-zero status to stop the GitLab job
elif [ "$statusIs" == "completed" ]; then
        echo " Experiment is Completed successfully "
else [ -z "$statusIs" ];
        exit 1  # Exit with a non-zero status for unexpected behavior
fi

echo "##########################################################################################################"
echo ""
