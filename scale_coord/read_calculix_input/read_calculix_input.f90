! ---------------------------------------------------------
! Module
! ---------------------------------------------------------
  module read_calculix_input_variables
  implicit none
! Local parameter
  integer,parameter :: CHAR_LEN = 100
  character(4),parameter :: name_ext_dat = '.dat'
! Variables
! --Input parameter
  character(CHAR_LEN), parameter :: controlfile_org = 'read_calculix_input.ctl'
  character(CHAR_LEN) :: controlfile
  character(CHAR_LEN), allocatable :: array_arg(:)
  character(CHAR_LEN) :: nloop_arg
!
  character(CHAR_LEN) :: inputfile_inp
  character(CHAR_LEN) :: outputfile_inp
  real(8) :: scalefact_inp  
  integer :: temporary_array_inp  

  integer :: num_node
  real(8),allocatable :: coord(:,:)  
  real(8),allocatable :: coord_scale(:,:)
!
  contains

! /////////////////////////////////////////////////////////
! Input parameter

  subroutine read_parameter
  integer :: narg, file_index, ios, n, i
  character(CHAR_LEN) :: file_name, arg_char
!
  write(6,*)'Reading input parameters...'
!
! Set control file
  narg = iargc()
  select case(narg)
    case(0)
    controlfile = controlfile_org
  case(1:)
    allocate(array_arg(narg))
    do n=1,narg
      call getarg(n,arg_char)
      array_arg(n) = adjustl(arg_char)
    end do
!
    controlfile = controlfile_org
    do n=1,narg
      if(array_arg(n) == '-cf' )then
        controlfile = array_arg(n+1)
      elseif(array_arg(n) == '-r' )then
        nloop_arg = array_arg(n+1)
      end if
    end do
  case default
    write(6,*)'ERROR: Number of arguments should be one!'
    write(6,*)'Program stop'
    stop
  end select
!
! Read control file
  write(6,*)'Control file: ',trim(controlfile)
  file_name  = trim(controlfile)
  file_index = 15
  open (file_index,file=file_name,status='unknown',form='formatted',iostat=ios)
    if(ios /= 0)then
      write(6,*)'Error!, Can not open: ',trim(file_name)
      stop
    end if
!
    read(file_index,*)
    read(file_index,*) inputfile_inp
    read(file_index,*) outputfile_inp
    read(file_index,*) scalefact_inp
    read(file_index,*) temporary_array_inp
!
!    read(file_index,*) density_input
!    read(file_index,*) radius_input
  close(file_index)
!
  return
  end subroutine read_parameter
!
! ---------------------------------------------------------
! Initilize variables
! ---------------------------------------------------------
!    subroutine initilize_read_fvexport_variables
!
!    num_node = 0
!    num_face = 0
!
!    factor_area(:) = 0.d0
!    factor_area(3) = 0.5d0
!    factor_area(4) = 1.0d0
!
!    return
!    end subroutine initilize_read_fvexport_variables
!
! ---------------------------------------------------------
! Allocate/Deallocate memory
! ---------------------------------------------------------
!    subroutine allocate_read_fvexport_variables
!
!    if( num_node > 0)then
!      if( .not. allocated(coord_node)    ) allocate( coord_node(3,num_node)    )
!      if( .not. allocated(pressure_node) ) allocate( pressure_node(num_node)   )
!      if( .not. allocated(velocity_node) ) allocate( velocity_node(3,num_node) )
!    end if
!
!    if( num_face > 0)then
!      if( .not. allocated(n_vertex)      ) allocate( n_vertex(num_face)        )
!      if( .not. allocated(face2node)     ) allocate( face2node(6,num_face)     )
!      if( .not. allocated(area_vec_face) ) allocate( area_vec_face(4,num_face) )
!      if( .not. allocated(velocity_face) ) allocate( velocity_face(3,num_face) )
!      if( .not. allocated(massflux_face) ) allocate( massflux_face(3,num_face) )
!    end if
!
!    return 
!    end subroutine allocate_read_fvexport_variables
!
!
!    subroutine deallocate_read_fvexport_variables
!
!    return
!    end subroutine deallocate_read_fvexport_variables
!
  end module read_calculix_input_variables
!
! /////////////////////////////////////////////////////////
! Program to read FV export file

	program read_calculix_input
  use read_calculix_input_variables
	implicit none
!
! Read parameter
  call read_parameter
!
! Convert coordinate
  call convert_coordinate
!
! Write data
  call write_data
!
	stop
	end program read_calculix_input
!
! /////////////////////////////////////////////////////////
! Read file of computational result by flow field solver

  subroutine convert_coordinate
  use read_calculix_input_variables
  implicit none
! Local variables
  integer :: file_index, err, n, i, i_dummy
  character(CHAR_LEN) :: file_name
  logical :: flag_break_tmp = .false.
!
  if( .not. allocated(coord) ) allocate( coord(3,temporary_array_inp) )
  num_node       = 1
  flag_break_tmp = .false.
!
  file_index = 20
  file_name = trim(adjustl(inputfile_inp))
  write(6,*)'Reading input file... ', trim(file_name)
  open(file_index,file=file_name,status='unknown',form='formatted')
    read(file_index,*) 
    read(file_index,*) 
    read(file_index,*) 
    read(file_index,*)
    read(file_index,*) 
    do while( .not. flag_break_tmp )
      read(file_index,*,iostat=err) i_dummy, (coord(i,num_node),i=1,3)
      if( err /= 0 ) then
        flag_break_tmp = .true.
        exit
      end if
      num_node = num_node + 1
    end do
    num_node = num_node - 1
  close(file_index)
!
  write(6,*)'Number of node: ',num_node
!
  if( .not. allocated(coord_scale) ) allocate( coord_scale(3,num_node) )
  do n=1,num_node
    coord_scale(1:3,n) = coord(1:3,n)*scalefact_inp
  end do
  deallocate(coord)
!
  return
  end subroutine convert_coordinate

! /////////////////////////////////////////////////////////
! Read file of computational result by flow field solver

  subroutine write_data
  use read_calculix_input_variables
  implicit none
! Local variables
  integer :: file_index, err, n, i
  character(CHAR_LEN) :: file_name
!
  file_index = 30
  file_name = trim(adjustl(outputfile_inp))
  write(6,*)'Writing data... ', trim(file_name)
  open(file_index,file=file_name,status='unknown',form='formatted')
!  write(file_index,*)'##Coordinate converted'
  do n=1,num_node
    write(file_index,"(i8,a1,es20.12,a1,es20.12,a1,es20.12)")n,',',coord_scale(1,n),',',coord_scale(2,n),',',coord_scale(3,n)
  end do
  close(file_index)
!
  return
  end subroutine write_data
!