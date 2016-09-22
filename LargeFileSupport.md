

### How to use git- large file support (git-lfs)


1. Install git-lfs, see for details https://git-lfs.github.com

1. Test if LFS works:
    1. if necessary, create an empty repository
        
            cd <repo>
            mkdir SANDBOX
            cd SANDBOX
            git init
    
    2. go into your repository (e.g. cd xyz/SANDBOX) and run the following lines:
        
            git lfs track "*.bsq"
            echo $null >> myblob.bsq
            git add myblob.bsq
            git commit -m "added test BLOB (myblob.bsq)"
            git lfs ls-files
        
    2. the printout of git lfs ls-files should look like:
    
            f00d900b19 - myblob.bsq



1. LFS in EnMAP-Box: Ensure the .gitattributes file exists in the root of your local branch and lists the 
file-types to be managed by LFS:

        ...
        *.bsq filter=lfs diff=lfs merge=lfs -text
        *.bip filter=lfs diff=lfs merge=lfs -text
        *.bil filter=lfs diff=lfs merge=lfs -text
        *.tif filter=lfs diff=lfs merge=lfs -text
        *.tiff filter=lfs diff=lfs merge=lfs -text
        *.img filter=lfs diff=lfs merge=lfs -text
        ...
    
        
        
        
        



