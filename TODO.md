# TODO Items

## Docker Build Optimization
- [ ] Reduce Docker build time from 544+ seconds
- [ ] Multi-stage build with dependency caching
- [ ] Use pre-built base images with ML libraries
- [ ] Optimize requirements.txt (remove unused packages)
- [ ] Use Docker BuildKit cache mounts effectively
- [ ] Fix Windows path issues with data copying

## Performance Optimization
- [ ] Implement incremental document indexing
- [ ] Add file change detection for faster startups
- [ ] Optimize embedding generation and caching
- [ ] Background indexing service

## K8s Improvements
- [ ] Add persistent volumes for data
- [ ] Implement proper health checks
- [ ] Add horizontal pod autoscaling
- [ ] Set up ingress controller
- [ ] Add monitoring and logging