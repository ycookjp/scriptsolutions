# -*- config: utf8 -*-
'''AwsResourceOperator module.

Copyright ycookjp
https://github.com/ycookjp/

'''

import boto3

class AwsResourceOperator:
    '''Base class for operating AWS resource.
    
    '''
    def get_status(self, resource_id: str):
        '''Gets resource status.
        
        Args:
            resource_id (str): Resource id.
        
        Returns:
            Returns resource status.
        
        '''
        pass
    
    def _get_client(self, service_name: str, region_name: str,
                    access_key_id: str=None, secret_access_key: str=None):
        '''Gets boto3 client.
        
        Args:
            seervice_name (str): service name such as ec2, rds ...
            aws_access_key_id (str): access key id.
            aws_secret_access_key (str): secret access key.
            region_name (str): region name.
        
        Returns:
            Returns boto3's client instance.
        
        '''
        client = boto3.client(service_name, aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key, region_name=region_name)
        
        return client
    
    def start(self, instance_id: str):
        '''Starts AWS service instance.
        
        Starts AWS service instance. This method is a abstruct method.
        
        Args:
            instance_id (str): Instance ID.
        
        '''
        pass
    
    def start_resources(self, instance_ids: list):
        '''Starts AWS resources.
        
        Starts AWS resources. This method is a abstruct method.
        
        Args:
            instance_ids (str ...): Instance IDs
        
        '''
        pass
    
    def stop(self, instance_id: str):
        '''Stops AWS resource instance.
        
        Stops AWS resource instance. This method is a abstruct method.
        
        Args:
            instance_id (str): Instance ID
        
        '''
        pass
    
    def stop_resources(self, instance_ids: list):
        '''Stops AWS resources.
        
        Stops AWS resources. This method is a abstruct method.
        
        Args:
            instance_ids (str ...): Instance IDs
        
        '''
        pass

class AwsEc2InstanceOperator(AwsResourceOperator):
    '''Operator class for EC2 instance.
    
    '''
    _client = None
    '''Boto3 ec2 client.
    '''
    
    def __init__(self, region_name: str, access_key_id: str=None,
                 secret_access_key: str=None):
        '''Constructor.
        
        '''
        self._client = self._get_client('ec2', region_name, access_key_id,
                                        secret_access_key)
    
    def get_status(self, ec2_instance_id: str):
        '''Gets EC2 instance status.
        
        Args:
            ec2_instance_id (str): EC2 instance id.
        
        Returns:
            Returns EC2 instance id status name.
            Status name is one of 'pending', 'running', 'shutting-down',
            'terminated', 'stopping', 'stopped'.
        
        '''
        response = self._client.describe_instance_status(InstanceIds=[ec2_instance_id])
        
        status = None
        if len(response['InstanceStatuses']) > 0:
            status = response['InstanceStatuses'][0]['InstanceState']['Name']
        
        return status

    def start(self, instance_id: str):
        '''Starts EC2 instance.
        
        Args:
            instance_id (str): EC2 instance id.
        
        '''
        self.start_resources([instance_id])
    
    def start_resources(self, instance_ids: list):
        '''Starts EC2 instances.
        
        Args:
            instance_ids (str ...): EC2 instance IDs
        
        '''
        self._client.start_instances(InstanceIds=instance_ids)
    
    def stop(self, instance_id: str):
        '''Stops EC2 instance.
        
        Args:
            instance_id (str): EC2 instance ID.
        
        '''
        self.stop_resources([instance_id])
    
    def stop_resources(self, instance_ids: list):
        '''Stops EC2 instances.
        
        Args:
            instance_ids (str ...): EC2 instance IDs.
        
        '''
        self._client.stop_instances(InstanceIds=instance_ids)

class AwsRdsDbClusterOperator(AwsResourceOperator):
    '''Operator class for RDS DB cluster.
    
    '''
    _client = None
    '''Boto3 rds client.
    '''
    
    def __init__(self, region_name: str, access_key_id: str=None,
                 secret_access_key: str=None):
        '''Constructor.
        
        '''
        self._client = self._get_client('rds', region_name, access_key_id,
                                        secret_access_key)
    
    def get_status(self, db_cluster_id: str):
        '''Gets RDS DB cluster status.
        
        Args:
            db_cluster_id (str): RDS DB cluster id.
        
        Returns:
            Returns RDS DB cluster status.
        
        '''
        response = self._client.describe_db_clusters(DBClusterIdentifier=db_cluster_id)
        
        status = None
        if len(response['DBClusters']) > 0:
            status = response['DBClusters'][0]['Status']
        
        return status
    
    def start(self, instance_id: str):
        '''Starts RDS cluster.
        
        Args:
            instance_id (str): RDS cluster ID.
        
        Returns:
            Number of started instance(s).
        
        '''
        count = 0
        status = self.get_status(instance_id)
        
        # starts cluster instance only if status is stopped
        if status == 'stopped':
            self._client.start_db_cluster(DBClusterIdentifier=instance_id)
            count = count + 1
        
        return count
    
    def start_resources(self, instance_ids: list):
        '''Starts RDS clusters.
        
        Args:
            instance_ids (list): RDS cluster IDs
        
        Returns:
            Number of started instance(s).
        
        '''
        count = 0
        
        for instance_id in instance_ids:
            result = self.start(instance_id)
            count = count + result
        
        return count
    
    def stop(self, instance_id: str):
        '''Stops RDS cluster.
        
        Args:
            instance_id (str): RDS cluster ID.
        
        Returns:
            Number of stopped instance(s).
        
        '''
        count = 0
        status = self.get_status(instance_id)
        
        # Stops cluster instance only if status is available
        if status == 'available':
            self._client.stop_db_cluster(DBClusterIdentifier=instance_id)
            count = count + 1
        
        return count
    
    def stop_resources(self, instance_ids: list):
        '''Stops RDS clusters.
        
        Args:
            instance_ids (str ...): RDS cluster IDs.
        
        Returns:
            Number of stopped instance(s).
        
        '''
        count = 0
        
        for instance_id in instance_ids:
            result = self.stop(instance_id)
            count = count + result
            
        return count

class AwsRdsDbInstanceOperator(AwsResourceOperator):
    '''Operator class for RDS instance.
    
    '''
    _client = None
    '''Boto3 rds client.
    '''
    
    def __init__(self, region_name: str, access_key_id: str=None,
                 secret_access_key: str=None):
        '''Constructor.
        
        '''
        self._client = self._get_client('rds', region_name,access_key_id,
                                        secret_access_key)
    
    def get_status(self, db_instance_id: str):
        '''Gets RDS DB instance status.
        
        Args:
            db_instance_id (str): RDS DB instance id.
        
        Returns:
            Returns RDS DB instance status.
        
        '''
        response = self._client.describe_db_instances(DBInstanceIdentifier=db_instance_id)
        
        status = None
        if len(response['DBInstances']) > 0:
            status = response['DBInstances'][0]['DBInstanceStatus']
        
        return status
    
    def start(self, instance_id: str):
        '''Starts RDS instance.
        
        Args:
            instance_id (str): RDS instance ID.
        
        Returns:
            Number of started instance(s).
        
        '''
        count = 0
        status = self.get_status(instance_id)
        
        # starts cluster instance only if status is stopped
        if status == 'stopped':
            self._client.start_db_instance(DBInstanceIdentifier=instance_id)
            count = count + 1
        
        return count
    
    def start_resources(self, instance_ids: list):
        '''Starts RDS instances.
        
        Args:
            instance_ids (list): RDS instance IDs
        
        '''
        for instance_id in instance_ids:
            self.start(instance_id)
    
    def stop(self, instance_id: str):
        '''Stops RDS instance.
        
        Args:
            instance_id (str): RDS instance ID.
        
        Returns:
            Number of stopped instance(s).
        
        '''
        count = 0
        status = self.get_status(instance_id)
        
        # starts cluster instance only if status is available
        if status == 'available':
            self._client.stop_db_instance(DBInstanceIdentifier=instance_id)
            count = count + 1
        
        return count
    
    def stop_resources(self, instance_ids: list):
        '''Stops RDS instances.
        
        Args:
            instance_ids (str ...): RDS instance IDs.
        
        Returns:
            Number of stopped instance(s).
        
        '''
        for instance_id in instance_ids:
            self.stop(instance_id)

class AwsResourceOperatorFactory:
    '''Factory class for generating AwsResourceOperator instance.
    
    '''
    
    @staticmethod
    def create(resource_type: str, region_name: str,
               access_key_id: str=None, secret_access_key: str=None):
        '''Creates AWS instance operator's instance.
        
        Args:
            service_name (str): AWS service name. Available service names
                are followings things.
                - ec2.instance
                - rds.db_cluster
                - rds.db_instance
        
        '''
        
        operator: AwsResourceOperator = None
        
        if resource_type == 'ec2.instance':
            operator = AwsEc2InstanceOperator(
                    region_name, access_key_id, secret_access_key)
        elif resource_type == 'rds.db_cluster':
            operator = AwsRdsDbClusterOperator(
                    region_name, access_key_id,secret_access_key)
        elif resource_type == 'rds.db_instance':
            operator = AwsRdsDbInstanceOperator(
                    region_name, access_key_id,secret_access_key)
        else:
            raise RuntimeError(f'Cloud not create AwsResourceOperator class from class name:{resource_type}')

        return operator
