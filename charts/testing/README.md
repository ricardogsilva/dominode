# Testing environment

This document serves as tutorial to generate testing infrastructure, similar with staging environment in your local cluster. It will be written as step by step approach rather than orchestrator scripts in order to test each components.

All shell commands assumes that it is executed from within this folder.

Requirements:
- Node with native NFS server enabled
- Local service discovery or ingress capable of resolving host name to machine IP.`

# Setting up NFS Server

Set appropriate permission for the NFS exports directory (config file in `/etc/exports`). See sample in [ci/nfs/exports](ci/nfs/exports).

You must:
- Specify which (native) machine directory to exports. In the example `/exports/s3data`
- Specify access control. The share must be accessible by machine IP of the nodes in the cluster and pods' cluster IP.
- The share mechanism assumes that the pod who can mount the share will gain total control of the folder being shared. Since the pods currently assumes root user, the folder will be set using root user of the pod.

After editing `/etc/exports`. Apply the changes.

In ubuntu:
```
sudo exportfs -rasv
```

Test by doing manual mount first. Create directory `/mnt/test` and do mount.

```
mkdir -p /mnt/test
mount <nfs-server-address:/exports/s3data /mnt/test
```

Check that you can read/write in the mounted directory `/mnt/test`. When done, unmount the folder:

```
umount /mnt/test
```

# Preparing chart orchestration

Before proceeding, if you want to use helm to generate k8s manifests, then make sure you update the dependencies.

```
# Add Bitnami repo if you haven't
helm repo add bitnami https://charts.bitnami.com/bitnami
helm dependency update
```

# Generating shared volume for Minio and geospatial data store

Minio is used for the user-facing file uploader/manager. The bucket where the user store the files should be used as geoserver spatial data store (files) and mounted inside GeoServer and GeoNode pods. We need to define this volume first, because we are going to patch it and used it later for the corresponding pods.

Before we mount the NFS volumes to the pods, we need to declare it.

Copy [ci/volume-share-values.yaml](ci/volume-share-values.yaml) and modify it to your cluster/nodes. The file only have relevant sections for this phase.

Store the modified values file wherever you like, but we are going to assume it's saved in `volume-share-values.yaml`

Execute to generate the manifests:

```
helm install volume-share . -f volume-share-values.yaml
```

Note that the command above will install the release `volume-share` (the phase name) in the current default namespace.

Confirm that the pv and pvc are generated:

```
kubectl get pv pv-nfs-share
kubectl get pvc nfs-share-volume
```

If the pv status is not BOUND, check your NFS share permissions.
For the pvc status, it's ok to not bound, because we don't have any pod yet.

You can continue the other phase if you prefer to create the pods first and come back to this section to check the status.

# (Optional) Generating shared NFS volume for media folder and GeoServer (config) data directory

It is also possible to mount the media folder and/or GeoServer data directory into the NFS share. 
This setup might be useful in the case of multi node cluster since the pod now be able to mount with ReadWriteMany access mode.

By using the same volume-share-values.yaml file you can toggle to true the key `mediaShare.enabled` and
`geoserverDataDirShare.enabled`. For the path mapping, if you put the folder inside the same folder where you choose minio data directory,
then minio will also display the folder as a bucket if you have the access to view it (as administrator).
If this is not you want, consider set up a different NFS share path and modify `/etc/exports` accordingly.

Note that either way, you need to make sure that the folder exists before deploying the manifests via helm because you are manually 
provisioning the volumes. 

Once you are ready, you can upgrade the release:

```
helm upgrade volume-share . -f volume-share-values.yaml
```

# Instantiating MinIO

In our use case, we instantiate Minio using helm charts and assign the corresponding data directory to be handled by Minio (from our NFS server).

Copy [ci/minio-values.yaml](ci/minio-values.yaml) and modify it to your cluster/nodes. The file only have relevant sections for this phase.

Store the modified values file wherever you like, but we are going to assume it's saved in `minio-values.yaml`

Take extra care for values `minio.global.minio.accessKey` and `minio.global.minio.secretKey` if you use it to generate live server as it should contain very secret string.

Execute to generate the manifests:

```
helm install minio . -f minio-values.yaml
```

Above command will install Minio instance. Check that the deployment succeed:

```
kubectl get deployment minio
```

You can also wait for the rollout status to finish:

```
kubectl rollout status deployment minio
```

If it says "minio" successfully rolled out, that means the minio instance is able to claim the NFS share we defined previously.
If the deployment success but the pods are not generated, check the pod logs and make sure that the 
volume claim `nfs-share-volume` has been correctly bound. If not, check your NFS permission settings.

After Minio successfully rollout, you must define how it can be accessed according to your cluster network policy.
The minio chart supports ingress and headless service and the overall settings can be seen in [their Github Readme](https://github.com/bitnami/charts/tree/master/bitnami/minio).

You can define ingress or service resources outside the helm charts installation (so it can be detached, independent by installation), or you can generate it
together with the chart since it supports it. In the values example, there is an ingress section that you can modify. 
You may want to change `minio.ingress.hosts[0].name` according to your chosen hostname.

# Instantiating Dominode app

We instantiate dominode app using helm charts and mount extra volumes in the pods.

Copy [ci/dominode-values.yaml](ci/dominode-values.yaml) and modify it to your cluster/nodes. The file only have relevant sections for this phase.

Store the modified values file wherever you like, but we are going to assume it's saved in `dominode-values.yaml`

The values that you want to change are typically secret/credentials based keys and also the site/host name.

Execute to generate the manifests:

```
helm install dominode . -f dominode-values.yaml
```

Above command will install Dominode instance. Check that the deployment succeed:

```
kubectl get deployment
```

You should see several deployment with `dominode-` prefix. These are Dominode components.

You can also wait for the rollout status of specific deployment to finish:

```
kubectl rollout status deployment dominode-geonode
```

It might take time for the whole stack to be fully loaded, but the deployment `dominode-geonode` should be the last to rollout.
So you can use that status as indicator that everything is running.

Generate ingress resources or services with the same site/host name that you used in the values file.
If you want, you can also generate the ingress as part of the release. The key is set in `dominode.geonode.ingress`.
Make sure the host name also match. 

# (Optional) Using shared NFS volume for media folder and GeoServer (config) data directory

In the previous optional step we generated persistent volume using NFS share. Dominode chart will make a certain volume claim.
If there are no volumes available, dynamic provisioner will generate the volume.
In case of this optional step, we already generate the persistent volume, we just need to tell 
Dominode to use it.

There is no need to change the `dominode-values.yaml` because the claim name is certain.
The persistent volumes were created in the `volume-share-values.yaml` step and is annotated 
so that the respective claim name will claim said volume. One minor exception would be for 
GeoServer Data Directory because the claim name is dynamically generated from the helm release name.
However if you choose release name `dominode` as used in the previous step, the claim name will
be the same with the default value, which is `dominode-geoserver-geoserver-data-dir`.

Confirm that the volumes are claimed by running:

```
kubectl get pv
```

All the volumes should be bound after you finished installing Dominode helm charts.

# Running bootstrap commands

We run the bootstrap commands either using k8s job manifests or via helm charts.

Copy [ci/bootstrapper-values.yaml](ci/bootstrapper-values.yaml) and modify it to your cluster/nodes. The file only have relevant sections for this phase.

Store the modified values file wherever you like, but we are going to assume it's saved in `bootstrapper-values.yaml`

The values that you will change are typically the bootstrapper config file, in the form of INI format.
You can either use Helm template to use existing helm values, or you can hardcode the config directly in the values file.

Execute to generate the manifests:

```
helm install bootstrapper . -f bootstrapper-values.yaml
```

Now, since k8s job currently works in such a way that it doesn't clean by itself when it is completed, you can't edit 
the bootstrapper release using `helm upgrade` if in the future you modify the values file or charts.
Instead, you need to delete the release and install it again, like this:

```
helm uninstall bootstrapper
helm install bootstrapper . -f bootstrapper-values.yaml
```

Once the resources are declared, the k8s job will control the pod and restart it if the job failed.
You can check the completion of the job by running:

```
kubectl get job dominode-bootstrapper 
```

If it completes, the column COMPLETIONS should indicate 1/1.
Alternatively, you can check the status in detail by using `kubectl describe`

```
kubectl describe job dominode-bootstrapper
```

If it describes **Job completed** in the Events sections, then the job has completed.

You can delete or let the completed Job resource in the cluster. 
Either way is fine if you prefer to keep the logs. But completed jobs can't be restarted. 
You need to uninstall the release and install it again if you want to rerun the job.
