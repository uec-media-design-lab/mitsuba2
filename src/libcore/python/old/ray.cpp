#include <mitsuba/render/fwd.h>
#include <mitsuba/core/ray.h>
#include <mitsuba/python/python.h>

MTS_PY_EXPORT_STRUCT(Ray) {
    MTS_IMPORT_TYPES()
    MTS_PY_CHECK_ALIAS(Ray3f, m) {
        auto ray = py::class_<Ray3f>(m, "Ray3f", D(Ray))
            .def(py::init<>(), "Create an unitialized ray")
            .def(py::init<const Ray3f &>(), "Copy constructor", "other"_a)
            .def(py::init<Point3f, Vector3f, Float, const Wavelength &>(),
                D(Ray, Ray, 5), "o"_a, "d"_a, "time"_a, "wavelengths"_a)
            .def(py::init<Point3f, Vector3f, Float, Float, Float, const Wavelength &>(),
                D(Ray, Ray, 6), "o"_a, "d"_a, "mint"_a, "maxt"_a, "time"_a, "wavelengths"_a)
            .def(py::init<const Ray3f &, Float, Float>(),
                D(Ray, Ray, 7), "other"_a, "mint"_a, "maxt"_a)
            .def("update", &Ray3f::update, D(Ray, update))
            .def("__call__", &Ray3f::operator(), D(Ray, operator, call))
            .def_field(Ray3f, o,           D(Ray, o))
            .def_field(Ray3f, d,           D(Ray, d))
            .def_field(Ray3f, d_rcp,       D(Ray, d_rcp))
            .def_field(Ray3f, mint,        D(Ray, mint))
            .def_field(Ray3f, maxt,        D(Ray, maxt))
            .def_field(Ray3f, time,        D(Ray, time))
            .def_field(Ray3f, wavelengths, D(Ray, wavelengths))
            .def_repr(Ray3f);
        bind_slicing_operators<Ray3f, Ray<ScalarPoint3f, scalar_spectrum_t<Spectrum>>>(ray);
    }

    MTS_PY_CHECK_ALIAS(RayDifferential3f, m) {
        py::class_<RayDifferential3f, Ray3f>(m, "RayDifferential3f", D(RayDifferential))

            .def(py::init<Ray3f &>(), "ray"_a)
            .def(py::init<Point3f, Vector3f, Float, const Wavelength &>(),
                 "Initialize without differentials.",
                 "o"_a, "d"_a, "time"_a, "wavelengths"_a)
            .def("scale_differential", &RayDifferential3f::scale_differential,
                 "amount"_a, D(RayDifferential, scale_differential))
            .def_field(RayDifferential3f, o_x, D(RayDifferential, o_x))
            .def_field(RayDifferential3f, o_y, D(RayDifferential, o_y))
            .def_field(RayDifferential3f, d_x, D(RayDifferential, d_x))
            .def_field(RayDifferential3f, d_y, D(RayDifferential, d_y))
            .def_field(RayDifferential3f, has_differentials, D(RayDifferential, has_differentials));
    }
}