import aws_cdk.aws_ec2 as ec2

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core
from aws_cdk import core as cdk


class SubnetStack(cdk.Stack):
    def __init__(
        self, scope: cdk.Construct, construct_id: str, **kwargs
    ) -> None:
        super().__init__(
            scope,
            construct_id,
            description="ThreeTierVPC experiment",
            **kwargs
        )

        # 3-Tier VPC from https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/README.html?highlight=internet%20gateway#advanced-subnet-configuration
        # Roughly along the lines of this layout:
        # https://content.aws.training/wbt/nwcnmv/en/x2/1.0.0/assets/mkw2mYPlFyk2-eeN_bXan0Tx3gMyKPMM2.png
        vpc = ec2.Vpc(
            self,
            "TheVPC",
            # 'cidr' configures the IP range and size of the entire VPC.
            # The IP space will be divided over the configured subnets.
            cidr="10.0.0.0/21",
            # 'maxAzs' configures the maximum number of availability zones to use
            max_azs=3,
            # 'subnetConfiguration' specifies the "subnet groups" to create.
            # Every subnet group will have a subnet for each AZ, so this
            # configuration will create `3 groups × 3 AZs = 6` subnets.
            ## Comment ^^ this above doesn't appear to be correct, only 2 of each
            ## seems to be created (two AZ used) when this stack is deployed currently
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    # 'subnetType' controls Internet access, as described above.
                    subnet_type=ec2.SubnetType.PUBLIC,
                    # 'name' is used to name this particular subnet group. You will have to
                    # use the name for subnet selection if you have more than one subnet
                    # group of the same type.
                    name="Ingress",
                    # 'cidrMask' specifies the IP addresses in the range of of individual
                    # subnets in the group. Each of the subnets in this group will contain
                    # `2^(32 address bits - 24 subnet bits) - 2 reserved addresses = 254`
                    # usable IP addresses.
                    #
                    # If 'cidrMask' is left out the available address space is evenly
                    # divided across the remaining subnet groups.
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    cidr_mask=24,
                    name="Application",
                    subnet_type=ec2.SubnetType.PRIVATE,
                ),
                ec2.SubnetConfiguration(
                    cidr_mask=28,
                    name="Database",
                    subnet_type=ec2.SubnetType.ISOLATED,
                    # 'reserved' can be used to reserve IP address space. No resources will
                    # be created for this subnet, but the IP range will be kept available for
                    # future creation of this subnet, or even for future subdivision.
                    reserved=True,
                ),
            ],
        )
