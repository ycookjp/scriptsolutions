# -*- config: utf8 -*-
'''AwsResourceOperator module.

Copyright ycookjp
https://github.com/ycookjp/

'''

import boto3
import logging

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
        
        Returns:
            Number of started instance(s).
        
        Raises:
            Exception: Raises exception if fail to start service instance.
        
        '''
        pass
    
    def start_resources(self, instance_ids: list):
        '''Starts AWS resources.
        
        Starts AWS resources. This method is a abstruct method.
        
        Args:
            instance_ids (str ...): Instance IDs
        
        Returns:
            Number of started instance(s).
        
        Raises:
            Exception: Raises exception if fail to start service instance
                at latest time.
        
        '''
        pass
    
    def stop(self, instance_id: str):
        '''Stops AWS resource instance.
        
        Stops AWS resource instance. This method is a abstruct method.
        
        Args:
            instance_id (str): Instance ID
        
        Returns:
            Number of stopped instance(s).
        
        Raises:
            Exception: Raises exception if fail to stop service instance.
        
        '''
        pass
    
    def stop_resources(self, instance_ids: list):
        '''Stops AWS resources.
        
        Stops AWS resources. This method is a abstruct method.
        
        Args:
            instance_ids (str ...): Instance IDs
        
        Returns:
            Number of stopped instance(s).
        
        Raises:
            Exception: Raises exception if fail to stop service instance
                at latest time.
        
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
        
        Sets boto3 ec2 client to _client field.
        
        Args:
            region_name (str): regian name.
            access_key_id (str, optional): access key id.
            secret_access_key (str, optional): secret access key.
        
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
        
        Returns:
            Number of started instance(s).
        
        Raises:
            Exception: Raises exception if fail to start EC2 instance.
        
        '''
        count = 0

        self._client.start_instances(InstanceIds=[instance_id])
        count = count + 1
        logging.info(f'ec2: \'{instance_id}\' starting ...')
        
        return count
    
    def start_resources(self, instance_ids: list):
        '''Starts EC2 instances.
        
        Args:
            instance_ids (str ...): EC2 instance IDs
        
        Returns:
            Number of started instance(s).
        
        Raises:
            Exception: raises exception if fail to start EC2 instance
                at latest time.
        
        '''
        count = 0
        error = None
        
        for instance_id in instance_ids:
            try:
                result = self.start(instance_id)
                count = count + result
            except Exception as e:
                error = e
        
        if error != None:
            raise error
        
        return count

    def stop(self, instance_id: str):
        '''Stops EC2 instance.
        
        Args:
            instance_id (str): EC2 instance ID.
        
        Returns:
            Number of stopped instance(s).
        
        Raises:
            Exception: Raises exception if fail to stop EC2 instance.
        
        '''
        count = 0
        
        self._client.stop_instances(InstanceIds=[instance_id])
        count = count + 1
        logging.info(f'ec2: \'{instance_id}\' stopping ...')
        
        return count
    
    def stop_resources(self, instance_ids: list):
        '''Stops EC2 instances.
        
        Args:
            instance_ids (str ...): EC2 instance IDs.
        
        Returns:
            Number of stopped instance(s).
        
        Raises:
            Exception: Raises exception if fail to stop EC2 instance
                at latest time.
        
        '''
        count = 0
        error = None
        
        for instance_id in instance_ids:
            try:
                result = self.stop(instance_id)
                count = count + result
            except Exception as e:
                error = e
        
        if error != None:
            raise error
        
        return count

class AwsRdsDbClusterOperator(AwsResourceOperator):
    '''Operator class for RDS DB cluster.
    
    '''
    _client = None
    '''Boto3 rds client.
    '''
    
    def __init__(self, region_name: str, access_key_id: str=None,
                 secret_access_key: str=None):
        '''Constructor.
        
        Sets boto3 rds client to _client field.
        
        Args:
            region_name (str): regian name.
            access_key_id (str, optional): access key id.
            secret_access_key (str, optional): secret access key.
        
        '''
        self._client = self._get_client('rds', region_name, access_key_id,
                                        secret_access_key)
    
    def get_status(self, db_cluster_id: str):
        '''Gets RDS DB cluster status.
        
        Args:
            db_cluster_id (str): RDS DB cluster id.
        
        Returns:
            Returns RDS DB cluster status name.
            Status name is on of 'available', 'backing-up', 'backtracking',
            'cloning-failed', 'creating', 'deleting', 'failing-over',
            'inaccessible-encryption-credentials'.
            'inaccessible-encryption-credentials-recoverable', 'maintenance',
            'migrating', 'migration-failed', 'modifying', 'promoting',
            'renaming', 'resetting-master-credentials', 'starting', 'stopped',
            'stopping', 'storage-optimization', 'update-iam-db-auth',
            'upgrading'.
        
        '''
        response = self._client.describe_db_clusters(DBClusterIdentifier=db_cluster_id)
        
        status = None
        if len(response['DBClusters']) > 0:
            status = response['DBClusters'][0]['Status']
        
        return status
    
    def start(self, instance_id: str):
        '''Starts RDS DB cluster.
        
        If RDS DB cluster status is 'stopped', then starts RDS DB cluster.
        Else do nothing.
        
        Args:
            instance_id (str): RDS DB cluster ID.
        
        Returns:
            Number of started cluster(s).
        
        Raises:
            Exception: Raises exception if fail to start RDS cluster.
        
        '''
        count = 0
        status = self.get_status(instance_id)
        
        # starts cluster instance only if status is stopped
        if status == 'stopped':
            self._client.start_db_cluster(DBClusterIdentifier=instance_id)
            count = count + 1
            logging.info(f'RDS DB cluster: \'{instance_id}\' starting ...')
        
        return count
    
    def start_resources(self, instance_ids: list):
        '''Starts RDS DB clusters.
        
        If RDS DB cluster status is 'stopped', then starts RDS DB cluster.
        Else do nothing.
        
        Args:
            instance_ids (list): RDS DB cluster IDs
        
        Returns:
            Number of started cluster(s).
        
        Raises:
            Exception: Raises exception if fail to start RDS cluster at
                latest time.
        
        '''
        count = 0
        error = None
        
        for instance_id in instance_ids:
            try:
                result = self.start(instance_id)
                count = count + result
            except Exception as e:
                error = e
        
        if error != None:
            raise error
        
        return count
    
    def stop(self, instance_id: str):
        '''Stops RDS DB cluster.
        
        If RDS DB instance status is 'available', then stops RDS DB instance.
        Else do nothing.
        
        Args:
            instance_id (str): RDS DB cluster ID.
        
        Returns:
            Number of stopped RDS DB cluster.
        
        Raises:
            Exception: Raises exception if fail to stop RDS cluster.
        
        '''
        count = 0
        status = self.get_status(instance_id)
        
        # Stops cluster instance only if status is available
        if status == 'available':
            self._client.stop_db_cluster(DBClusterIdentifier=instance_id)
            count = count + 1
            logging.info(f'RDS DB cluster: \'{instance_id}\' stopping ...')
        
        return count
    
    def stop_resources(self, instance_ids: list):
        '''Stops RDS DB clusters.
        
        If RDS DB instance status is 'available', then stops RDS DB instance.
        Else do nothing.
        
        Args:
            instance_ids (str ...): RDS DB cluster IDs.
        
        Returns:
            Number of stopped RDS DB cluster(s).
        
        Raises:
            Exception: Raises exception if fail to stop RDS cluster at latest time.
        
        '''
        count = 0
        error = None
        
        for instance_id in instance_ids:
            try:
                result = self.stop(instance_id)
                count = count + result
            except Exception as e:
                error = e
        
        if error != None:
            raise error
        
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
        
        Sets boto3 rds client to _client instance variable.
        
        Args:
            region_name (str): regian name.
            access_key_id (str, optional): access key id.
            secret_access_key (str, optional): secret access key.
        
        '''
        self._client = self._get_client('rds', region_name,access_key_id,
                                        secret_access_key)
    
    def get_status(self, db_instance_id: str):
        '''Gets RDS DB instance status.
        
        Args:
            db_instance_id (str): RDS DB instance id.
        
        Returns:
            Returns RDS DB instance status name.
            Status name is one of 'available', 'backing-up',
            'configuring-enhanced-monitoring', 'configuring-iam-database-auth',
            'configuring-log-exports', 'converting-to-vpc', 'creating',
            'deleting', 'failed', 'inaccessible-encryption-credentials',
            'inaccessible-encryption-credentials-recoverable',
            'incompatible-network', 'incompatible-option-group',
            'incompatible-parameters', 'incompatible-restore',
            'insufficient-capacity', 'maintenance', 'modifying',
            'moving-to-vpc', 'rebooting', 'resetting-master-credentials',
            'renaming', 'restore-error', 'starting', 'stopped', 'stopping',
            'storage-full', 'storage-optimization', 'upgrading'.
        
        '''
        response = self._client.describe_db_instances(DBInstanceIdentifier=db_instance_id)
        
        status = None
        if len(response['DBInstances']) > 0:
            status = response['DBInstances'][0]['DBInstanceStatus']
        
        return status
    
    def start(self, instance_id: str):
        '''Starts RDS DB instance.
        
        If RDS DB instance status is stopped, then starts RDS DB instance.
        Else do nothing.
        
        Args:
            instance_id (str): RDS DB instance ID.
        
        Returns:
            Number of started instance(s).
        
        Raises:
            Exception: Raises exception if fail to start RDS instance.
        
        '''
        count = 0
        status = self.get_status(instance_id)
        
        # starts cluster instance only if status is stopped
        if status == 'stopped':
            self._client.start_db_instance(DBInstanceIdentifier=instance_id)
            count = count + 1
            logging.info(f'RDS instance: \'{instance_id}\' starting ...')
        
        return count
    
    def start_resources(self, instance_ids: list):
        '''Starts RDS DB instances.
        
        If RDS DB instance status is stopped, then starts RDS DB instance.
        Else do nothing.
        
        Args:
            instance_ids (list): RDS DB instance IDs
        
        Returns:
            Number of started instance(s).
        
        Raises:
            Exception: Raises exception if fail to start RDS DB instance
                at latest time.
        
        '''
        count = 0
        error = None
        
        for instance_id in instance_ids:
            try:
                result = self.start(instance_id)
                count = count + result
            except Exception as e:
                error = e
        
        if error != None:
            raise error
        
        return count
    
    def stop(self, instance_id: str):
        '''Stops RDS DB instance.
        
        If RDS DB instance status is available, then stops RDS DB instance.
        Else do nothing.
        
        Args:
            instance_id (str): RDS DB instance ID.
        
        Returns:
            Number of stopped instance(s).
        
        Raises:
            Exception: Raises exception if fail to stop RDS DB instance.
        
        '''
        count = 0
        status = self.get_status(instance_id)
        
        # starts cluster instance only if status is available
        if status == 'available':
            self._client.stop_db_instance(DBInstanceIdentifier=instance_id)
            count = count + 1
            logging.info(f'RDS instance: \'{instance_id}\' stopping ...')
        
        return count
    
    def stop_resources(self, instance_ids: list):
        '''Stops RDS DB instances.
        
        If RDS DB instance status is available, then stops RDS DB instance.
        Else do nothing.
        
        Args:
            instance_ids (str ...): RDS instance IDs.
        
        Returns:
            Number of stopped instance(s).
        
        Raises:
            Exception: Raises exception if fail to stop RDS DB instance
                at latest time.
        
        '''
        count = 0
        error = None
        
        for instance_id in instance_ids:
            try:
                result = self.stop(instance_id)
                count = count + result
            except Exception as e:
                error = e
        
        if error != None:
            raise error
        
        return count

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
        
        Returns:
            AwsResourceOperator: Returns created AWS instance operator's
                instance.
        
        Raises:
            RuntimeError: If service_name is incorrect.
        
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
